# Data Engineering Zoomcamp Module 6 Homework: Stream Processing

## Question 1: Redpanda version

Now let's find out the version of redpandas.

For that, check the output of the command ```rpk help``` inside the container. The name of the container is ```redpanda-1```.

Find out what you need to execute based on the ```help``` output.

What's the version, based on the output of the command you executed? (copy the entire version)

**Answer -> v24.2.18 **

![Question 1](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/06-streaming/pyflink/images/Qns%201.jpg)


## Question 2: Creating a topic

Before we can send data to the redpanda server, we need to create a topic. We do it also with the ```rpk``` command we used previously for figuring out the version of redpandas.

Read the output of ```help``` and based on it, create a topic with name ```green-trips```

What's the output of the command for creating a topic? Include the entire output in your answer.

**Answer -> Status OK **

![Question 2](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/06-streaming/pyflink/images/Qns%202.jpg)


## Question 3: Connecting to the Kafka server

We need to make sure we can connect to the server, so later we can send some data to its topics

First, let's install the kafka connector (up to you if you want to have a separate virtual environment for that)

```pip install kafka-python```
You can start a jupyter notebook in your solution folder or create a script

Let's try to connect to our server:
```
import json

from kafka import KafkaProducer

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

server = 'localhost:9092'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=json_serializer
)

producer.bootstrap_connected()
```
Provided that you can connect to the server, what's the output of the last command?

**Answer -> True **

![Question 3](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/06-streaming/pyflink/images/Qns%203.jpg)


## Question 4: Sending the Trip Data

Now we need to send the data to the ```green-trips``` topic

Read the data, and keep only these columns:

* 'lpep_pickup_datetime',
* 'lpep_dropoff_datetime',
* 'PULocationID',
* 'DOLocationID',
* 'passenger_count',
* 'trip_distance',
* 'tip_amount'
Now send all the data using this code:
```
producer.send(topic_name, value=message)
For each row (message) in the dataset. In this case, message is a dictionary.
```
After sending all the messages, flush the data:

```
producer.flush()
```

Use from time import time to see the total time

```
from time import time

t0 = time()

topic_name = 'green-trips'

for index, row in df.iterrows():
    message = {
        'lpep_pickup_datetime': row['lpep_pickup_datetime'],
        'lpep_dropoff_datetime': row['lpep_dropoff_datetime'],
        'PULocationID': row['PULocationID'],
        'DOLocationID': row['DOLocationID'],
        'passenger_count': row['passenger_count'],
        'trip_distance': row['trip_distance'],
        'tip_amount': row['tip_amount']
    }
    
    producer.send(topic_name, value=message)
    print(f"Sent: {message}")

producer.flush()
producer.close()

t1 = time()
took = t1 - t0
```
How much time did it take to send the entire dataset and flush?

**Answer -> 101.90 seconds **

![Question 4](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/06-streaming/pyflink/images/Qns%204.jpg)


## Question 5: Build a Sessionization Window

Now we have the data in the Kafka stream. It's time to process it.

* Copy ```aggregation_job.py``` and rename it to ```session_job.py```
* Have it read from ```green-trips``` fixing the schema
* Use a [session window](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/operators/windows/) with a gap of 5 minutes
* Use ```lpep_dropoff_datetime``` time as your watermark with a 5 second tolerance
* Which pickup and drop off locations have the longest unbroken streak of taxi trips?

**Answer -> 44 Trip Counts (PULocationID: 95, DOLocationID: 95) **

![Question 5](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/06-streaming/pyflink/images/Qns%205.jpg)

### session_job.py
```
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, TableEnvironment, StreamTableEnvironment
from pyflink.common.time import Duration

def create_events_aggregated_sink(t_env):
    table_name = 'green_trips_aggregated'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            PULocationID INTEGER,
            DOLocationID INTEGER,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            trip_count BIGINT,
            PRIMARY KEY (PULocationID, DOLocationID, session_start) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
        """
    t_env.execute_sql(sink_ddl)
    return table_name

def create_events_source_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            lpep_pickup_datetime TIMESTAMP(3),
            lpep_dropoff_datetime TIMESTAMP(3),
            PULocationID INTEGER,
            DOLocationID INTEGER,
            passenger_count INTEGER,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            event_watermark AS lpep_dropoff_datetime,
            WATERMARK FOR event_watermark AS event_watermark - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda-1:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
        """
    t_env.execute_sql(source_ddl)
    return table_name


def log_aggregation():
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(30 * 1000)
    env.set_parallelism(1)

    # Set up the table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    try:
        # Create Kafka table
        source_table = create_events_source_kafka(t_env)
        aggregated_table = create_events_aggregated_sink(t_env)

        # Query to find the longest unbroken streak of taxi trips
        t_env.execute_sql(f"""
        INSERT INTO {aggregated_table}
        SELECT
            PULocationID,
            DOLocationID,
            MIN(event_watermark) AS session_start,
            MAX(event_watermark) AS session_end,
            COUNT(*) AS trip_count
        FROM {source_table}
        GROUP BY
            PULocationID,
            DOLocationID,
            SESSION(event_watermark, INTERVAL '5' MINUTE);
        """).wait()

    except Exception as e:
        print("Writing records from Kafka to JDBC failed:", str(e))


if __name__ == '__main__':
    log_aggregation()
```

### Create Table green_trips_aggregated
```
CREATE TABLE green_trips_aggregated (
    PULocationID INTEGER,
    DOLocationID INTEGER,
    session_start TIMESTAMP(3),
    session_end TIMESTAMP(3),
    trip_count BIGINT,
    PRIMARY KEY (PULocationID, DOLocationID, session_start)
);
```

### SQL Query to find pickup and drop off locations have the longest unbroken streak of taxi trips.
```
select * from green_trips_aggregated
order by trip_count desc;
```
