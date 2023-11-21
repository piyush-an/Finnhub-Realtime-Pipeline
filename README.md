# finnhub-realtime-pipeline

The project is a streaming data pipeline based on Finnhub.io API/websocket real-time trading data processed by spark

## Architecture

All applications are containerized into Docker containers

**Data ingestion layer** - A containerized Python application named finnhub_producer connects to the Finnhub.io websocket. It encodes retrieved messages into Avro format, as specified in the `schemas/trades.avsc` file, and ingests messages into the Kafka broker.

**Message broker layer** - Messages from finnhub_producer are consumed by the Kafka broker located in the broker container.

**Stream processing layer** - A Spark cluster consisting of one master and worker node is set up. A PySpark application named processor is submitted to the Spark cluster manager, which delegates a worker for it. This application connects to the Kafka broker to retrieve messages, transforms them using Spark Structured Streaming, and loads them into Cassandra tables. The first query, which transforms trades into a feasible format, runs continuously, whereas the second query, involving aggregations, has a 5-second trigger.

**Serving database layer** - A Cassandra database stores and persists data from Spark jobs. Upon launching, the `cassandra-setup.cql` script runs to create the keyspace and tables.

**Visualization layer** - Grafana connects to the Cassandra database using HadesArchitect-Cassandra-Plugin and serves visualized data to users, exemplified in the Finnhub Sample BTC Dashboard. The dashboard refreshes every 500ms.


## Dashboard

You can access Grafana with a dashboard on localhost:3003


## Setup & deployment

