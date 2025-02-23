{{
    config(
        materialized='table'
    )
}}

with fhv_monthly_data as (
    select * from {{ ref('dim_fhv_trips') }}
),
fhv_filtered_data as (
    select 
        tripid,
        fhv_year,
        fhv_month,
        pickup_datetime,
        dropoff_datetime,
        TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) as trip_duration,
        pickup_location_id,
        dropoff_location_id,
        pickup_zone,  
        dropoff_zone
    from fhv_monthly_data
),
fhv_p90 as (
    SELECT 
        fhv_year,
        fhv_month,
        pickup_location_id,
        dropoff_location_id,
        pickup_zone,  
        dropoff_zone,
        trip_duration,
        PERCENTILE_CONT(trip_duration,0.9) OVER 
        (PARTITION BY fhv_year, fhv_month, pickup_location_id, dropoff_location_id, pickup_zone, dropoff_zone) AS p90
    FROM fhv_filtered_data
),
fhv_p90_distinct as (
    SELECT 
        distinct fhv_year,
        fhv_month,
        pickup_location_id,
        dropoff_location_id,
        pickup_zone,  
        dropoff_zone,
        p90
    FROM fhv_p90
),
fhv_p90_rank as (
    select
        fhv_year,
        fhv_month,
        pickup_zone,  
        dropoff_zone,
        p90,
        RANK() OVER (PARTITION BY pickup_zone ORDER BY p90 desc) AS rank
    from fhv_p90_distinct
    where fhv_year = 2019
    and fhv_month = 11
    and lower(pickup_zone) in ('newark airport', 'soho', 'yorkville east')
    order by pickup_zone
)

select * from fhv_p90_rank
where rank = 2
order by pickup_zone