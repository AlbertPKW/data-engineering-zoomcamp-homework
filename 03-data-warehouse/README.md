# Data Engineering Zoomcamp Module 3 Homework: Data Warehouse and BigQuery

## Big Query Homework 3
```
-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'Parquet',
  uris = ['gs://taxi-rides-ny-ap/yellow_tripdata_2024-*.parquet']
);


-- Check yellow trip data
SELECT * FROM sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata LIMIT 10;


-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned AS
SELECT * FROM sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata;


-- Check count of non-partitioned yellow trip data
SELECT COUNT(*) FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;


-- Check Estimated Query Size for PULocationID
SELECT COUNT(DISTINCT(PULocationID)) FROM sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata;
SELECT COUNT(DISTINCT(PULocationID)) FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;


-- Check Estimated Query Size for 1 column vs 2 columns
SELECT PULocationID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;
SELECT PULocationID, DOLocationID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;


-- Check records where fare amount is 0
SELECT COUNT(*) FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned
WHERE fare_amount=0;


-- Create a partitioned table from external table
CREATE OR REPLACE TABLE `sylvan-terra-447609-d6.nytaxi.yellow_tripdata_partitoned`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS (
  SELECT * FROM `sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata`
);


-- Find Distinct Vendor IDs from 1st-15th March
SELECT DISTINCT VendorID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned
WHERE tpep_dropoff_datetime BETWEEN PARSE_TIMESTAMP('%Y-%m-%d', '2024-03-01') AND PARSE_TIMESTAMP('%Y-%m-%d', '2024-03-15');

SELECT DISTINCT VendorID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_partitoned
WHERE tpep_dropoff_datetime BETWEEN PARSE_TIMESTAMP('%Y-%m-%d', '2024-03-01') AND PARSE_TIMESTAMP('%Y-%m-%d', '2024-03-15');
```

## Question 1
What is count of records for the 2024 Yellow Taxi Data?

**Answer -> 20,332,093**

![Question 1 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%201.jpg)

## Question 2
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

**Answer -> 0 MB for the External Table and 155.12 MB for the Materialized Table**

![Question 2A Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%202A%20(External%20Table).jpg)

![Question 2B Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%202B%20(Materialized%20Table).jpg)

## Question 3
Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?

```
SELECT PULocationID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;
SELECT PULocationID, DOLocationID FROM sylvan-terra-447609-d6.nytaxi.yellow_tripdata_non_partitoned;
```

**Answer -> BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.**

## Question 4
How many records have a fare_amount of 0?

**Answer -> 8,333**

![Question 4 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%204.jpg)

## Question 5
What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)

```
-- Create a partitioned table from external table
CREATE OR REPLACE TABLE `sylvan-terra-447609-d6.nytaxi.yellow_tripdata_partitoned`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS (
  SELECT * FROM `sylvan-terra-447609-d6.nytaxi.external_yellow_tripdata`
);
```

**Answer -> Partition by tpep_dropoff_datetime and Cluster on VendorID**

## Question 6
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

Choose the answer which most closely matches.

**Answer -> 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table**

![Question 6A Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%205A%20(Non%20Partitioned%20Table).jpg)

![Question 6B Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%205B%20(Partitioned%20Table).jpg)

## Question 7
Where is the data stored in the External Table you created?

**Answer -> GCP Bucket**

## Question 8
It is best practice in Big Query to always cluster your data:

**Answer -> False**

## Question 9
No Points: Write a SELECT count(*) query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

**Answer -> BigQuery estimates that it will process 0 bytes when running a SQL query on a materialized table because materialized tables are fully precomputed and stored as physical tables in BigQuery**

![Question 9 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/03-data-warehouse/images/Qns%209.jpg)
