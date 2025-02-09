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
