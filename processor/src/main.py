import os
import uuid
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, current_timestamp, unix_timestamp
from pyspark.sql.avro.functions import from_avro, to_avro
from pyspark.sql import functions as F


spark = SparkSession.builder \
    .appName("Finnhub") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.cassandra.auth.username", "cassandra") \
    .config("spark.cassandra.auth.password", "cassandra") \
    .getOrCreate()
    # .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1") \

# spark = SparkSession.builder \
#     .appName("Finnhub") \
#     .config("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "localhost")) \
#     .config("spark.cassandra.connection.port", os.getenv("CASSANDRA_PORT", 6379)) \
#     .config("spark.cassandra.auth.username", os.getenv("CASSANDRA_USERNAME", "cassandra")) \
#     .config("spark.cassandra.auth.password", os.getenv("CASSANDRA_PASSWORD", "cassandra")) \
#     .getOrCreate()
    # .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1") \

spark.sparkContext.setLogLevel("WARN")

avro_schema_file = "/opt/bitnami/spark/scripts/schemas/trades.avsc"
with open(avro_schema_file, "r") as file:
    avro_schema = file.read()

kafka_params = {
    "kafka.bootstrap.servers": "broker:29092",
    "subscribe": "market",
    "minPartitions": "1",
    "maxOffsetsPerTrigger": "1000",
    "useDeprecatedOffsetFetching": "false"
}

df = spark.readStream.format("kafka") \
    .options(**kafka_params) \
    .load()

expanded_df = df \
            .withColumn("avroData",from_avro(col("value"),avro_schema)) \
            .select("avroData.*") \
            .select(explode("data"),"type") \
            .select("col.*")

final_df = expanded_df \
    .withColumn("uuid", F.udf(lambda: str(uuid.uuid1()))()) \
    .withColumnRenamed("c", "trade_conditions") \
    .withColumnRenamed("p", "price") \
    .withColumnRenamed("s", "symbol") \
    .withColumnRenamed("t", "trade_timestamp") \
    .withColumnRenamed("v", "volume") \
    .withColumn("trade_timestamp", (col("trade_timestamp") / 1000).cast("timestamp")) \
    .withColumn("ingest_timestamp", current_timestamp())

query = final_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .start()

query = final_df.writeStream \
    .foreachBatch(lambda batchDF, batchID:
        batchDF.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="trades", keyspace="market") \
            .mode("append") \
            .save()
    ) \
    .outputMode("update") \
    .start()

summary_df = final_df \
    .withColumn("price_volume_multiply", F.col("price") * F.col("volume")) \
    .withWatermark("trade_timestamp", "15 seconds") \
    .groupBy("symbol") \
    .agg(F.avg("price_volume_multiply").alias("avg_price_volume_multiply"))

final_summary_df = summary_df \
    .withColumn("uuid", F.udf(lambda: str(uuid.uuid1()))()) \
    .withColumn("ingest_timestamp", current_timestamp()) \
    .withColumnRenamed("avg_price_volume_multiply", "price_volume_multiply")

query2 = final_summary_df \
    .writeStream \
    .trigger(processingTime='5 seconds') \
    .foreachBatch(lambda batchDF, batchID: 
        batchDF.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="running_averages_15_sec", keyspace="market") \
            .mode("append") \
            .save()
    ) \
    .outputMode("update") \
    .start()

# query = final_summary_df.writeStream \
#         .outputMode("complete") \
#         .format("console") \
#         .option("truncate", False) \
#         .start()



query.awaitTermination()


"""
To run this job, use the following command:
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.3,org.apache.spark:spark-avro_2.12:3.3.3,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 main.py
"""