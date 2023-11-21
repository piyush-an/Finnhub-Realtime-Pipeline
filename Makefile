build:
	docker compose build 

build-nc:
	docker compose build --no-cache

run:
	make down && docker compose up -d

spark-job:
	docker exec -ti spark-master /bin/bash -c "spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 scripts/main.py"

down:
	docker compose down --volumes --remove-orphans

stop:
	docker compose stop

KAFKA_BIN_DIR := ./kafka_2.13-3.6.0

k-download:
	wget https://dlcdn.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
	tar -xzf kafka_2.13-3.6.0.tgz
# rm -rf kafka_2.13-3.6.0.tgz

zk:
	${KAFKA_BIN_DIR}/bin/zookeeper-server-start.sh config/zookeeper.properties

start:
	${KAFKA_BIN_DIR}/bin/kafka-server-start.sh config/server.properties

topic:
	${KAFKA_BIN_DIR}/bin/kafka-topics.sh --create --topic market --if-not-exists --bootstrap-server localhost:9092

producer:
	${KAFKA_BIN_DIR}/bin/kafka-console-producer.sh --topic market --bootstrap-server localhost:9092

consumer:
	${KAFKA_BIN_DIR}/bin/kafka-console-consumer.sh --topic market --from-beginning --bootstrap-server localhost:9092

# export SPARK_HOME=/home/anku/sandbox/finnhub-streaming-data-pipeline-main/StreamProcessor/spark-3.5.0-bin-hadoop3
# export PATH=$SPARK_HOME/bin:$PATH
