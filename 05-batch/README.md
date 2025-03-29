# Data Engineering Zoomcamp Module 5 Homework: Batch Processing

## Question 1: Install Spark and PySpark

* Install Spark
* Run PySpark
* Create a local spark session
* Execute spark.version.

What's the output?

**Answer -> '3.4.4'**

```
import pyspark
from pyspark.sql import SparkSession

pyspark.__version__

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

![Question 1](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%201.jpg)

## Question 2: Yellow October 2024

Read the October 2024 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

**Answer -> 25MB**

```
output_path = 'data/pq/homework/yellow/2024/10/'

df_yellow = spark.read \
        .parquet('yellow_tripdata_2024-10.parquet')

df_yellow \
        .repartition(4) \
        .write.parquet(output_path, mode='overwrite')

ls -lh data/pq/homework/yellow/2024/10/
```

![Question 2](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%202.jpg)

## Question 3: Count records

How many taxi trips were there on the 15th of October?

Consider only trips that started on the 15th of October.

**Answer -> 125,567 (Closest Answer)**

```
df_yellow.registerTempTable('yellow_trips')

df_day_trips = spark.sql("""
SELECT 
    DATE(tpep_pickup_datetime) as pickup_date,
    COUNT(*) AS trips_count
FROM
    yellow_trips
WHERE
    tpep_pickup_datetime BETWEEN '2024-10-15 00:00:00' AND '2024-10-15 23:59:59'
GROUP BY
   1

df_day_trips.show()
""")
```

![Question 3](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%203.jpg)

## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

**Answer -> 162 (Closest Answer)**

```
df_longest_trip = spark.sql("""
SELECT
    VendorID,
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    timestampdiff(HOUR, tpep_pickup_datetime, tpep_dropoff_datetime) AS hours_diff
FROM
    yellow_trips
ORDER BY
   timestampdiff(HOUR, tpep_pickup_datetime, tpep_dropoff_datetime) DESC
LIMIT 3
""")

df_longest_trip.show()
```

![Question 4](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%204.jpg)

## Question 5: User Interface

Spark’s User Interface which shows the application's dashboard runs on which local port?

**Answer -> 4040**

![Question 5](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%205.jpg)

## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv```

Using the zone lookup data and the Yellow October 2024 data, what is the name of the LEAST frequent pickup location Zone?

**Answer -> Governor's Island/Ellis Island/Liberty Island**

```
df_zones = spark.read \
        .option("header", "true") \
        .csv('taxi_zone_lookup.csv')

df_result = df_yellow.join(df_zones, df_yellow.PULocationID == df_zones.LocationID)

df_result.registerTempTable('df_least_zone')

df_least_zone = spark.sql("""
SELECT
    PULocationID,
    Zone,
    COUNT(1) as frequency
FROM
    df_least_zone
GROUP BY
   1, 2
ORDER BY
   3 ASC
LIMIT 3
""")

df_least_zone.show()
```

![Question 6](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/05-batch/images/Qns%206.jpg)
