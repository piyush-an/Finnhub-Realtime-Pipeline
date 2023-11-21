FROM bitnami/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y curl

RUN pip install avro-python3==1.10.2 kafka-python==2.0.2

USER 1001

# RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar --output /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar
# RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-avro_2.12/3.5.0/spark-avro_2.12-3.5.0.jar --output /opt/bitnami/spark/jars/spark-avro_2.12-3.5.0.jar
# RUN curl https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.4.1/spark-cassandra-connector_2.12-3.4.1.jar --output /opt/bitnami/spark/jars/spark-cassandra-connector_2.12-3.4.1.jar
