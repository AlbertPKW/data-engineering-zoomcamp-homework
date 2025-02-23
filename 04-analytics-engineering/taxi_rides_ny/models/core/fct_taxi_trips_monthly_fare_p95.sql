{{
    config(
        materialized='table'
    )
}}

WITH trips_mth_data AS (
    SELECT 
        service_type,
        trip_distance,
        payment_type_description,
        pickup_datetime,
        EXTRACT(month FROM pickup_datetime) AS fare_month,
        EXTRACT(year FROM pickup_datetime) AS fare_year,
        fare_amount
    FROM {{ ref('fact_trips') }}
    WHERE fare_amount > 0
    AND trip_distance > 0
    AND lower(payment_type_description) IN ('cash', 'credit card')
),
trips_apr_2020 AS (
    SELECT * FROM trips_mth_data
    WHERE fare_month = 04
    AND fare_year = 2020
),
percentile_fares AS (
    SELECT 
        service_type,
        fare_year,
        fare_month,
        PERCENTILE_CONT(fare_amount,0.97) OVER (PARTITION BY service_type, fare_year, fare_month) AS p97,
        PERCENTILE_CONT(fare_amount,0.95) OVER (PARTITION BY service_type, fare_year, fare_month) AS p95,
        PERCENTILE_CONT(fare_amount,0.90) OVER (PARTITION BY service_type, fare_year, fare_month) AS p90,
    FROM trips_apr_2020
)
SELECT 
    distinct service_type,
    fare_year,
    fare_month,
    p97,
    p95,
    p90,
FROM percentile_fares
order by service_type
