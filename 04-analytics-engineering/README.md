<<<<<<< HEAD

=======
# Data Engineering Zoomcamp Module 4 Homework: Analytics Engineering

## Question 1: Understanding dbt model resolution

Provided you've got the following sources.yaml

```
version: 2

sources:
  - name: raw_nyc_tripdata
    database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
    schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
    tables:
      - name: ext_green_taxi
      - name: ext_yellow_taxi
```

with the following env variables setup where dbt runs:

```
export DBT_BIGQUERY_PROJECT=myproject
export DBT_BIGQUERY_DATASET=my_nyc_tripdata
```

What does this .sql model compile to?

```
select * 
from {{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}
```

**Answer -> select * from myproject.raw_nyc_tripdata.ext_green_taxi**

## Question 2: dbt Variables & Dynamic Models

Say you have to modify the following dbt_model (fct_recent_taxi_trips.sql) to enable Analytics Engineers to dynamically control the date range.

* In development, you want to process only the last 7 days of trips
* In production, you need to process the last 30 days for analytics

```
select *
from {{ ref('fact_taxi_trips') }}
where pickup_datetime >= CURRENT_DATE - INTERVAL '30' DAY
```

What would you change to accomplish that in a such way that command line arguments takes precedence over ENV_VARs, which takes precedence over DEFAULT value?

**Answer -> Update the WHERE clause to pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY**

## Question 3: dbt Data Lineage and Execution

Considering the data lineage below and that taxi_zone_lookup is the only materialization build (from a .csv seed file):

![Lineage](https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/cohorts/2025/04-analytics-engineering/homework_q2.png)

Select the option that does NOT apply for materializing fct_taxi_monthly_zone_revenue:

**Answer -> dbt run --select models/staging/+**

## Question 4: dbt Macros and Jinja

Consider you're dealing with sensitive data (e.g.: [PII](https://en.wikipedia.org/wiki/Personal_data)), that is only available to your team and very selected few individuals, in the ```raw``` layer of your DWH (e.g: a specific BigQuery dataset or PostgreSQL schema),

* Among other things, you decide to obfuscate/masquerade that data through your staging models, and make it available in a different schema (a ```staging layer```) for other Data/Analytics Engineers to explore

* And optionally, yet another layer (```service layer```), where you'll build your dimension (```dim_```) and fact (```fct_```) tables (assuming the [Star Schema dimensional modeling](https://www.databricks.com/glossary/star-schema)) for Dashboarding and for Tech Product Owners/Managers

You decide to make a macro to wrap a logic around it:

```
{% macro resolve_schema_for(model_type) -%}

    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}

{%- endmacro %}
```

And use on your staging, dim_ and fact_ models as:

```
{{ config(
    schema=resolve_schema_for('core'), 
) }}
```

That all being said, regarding macro above, select all statements that are true to the models using it:

***
* Setting a value for DBT_BIGQUERY_TARGET_DATASET env var is mandatory, or it'll fail to compile
* When using core, it materializes in the dataset defined in DBT_BIGQUERY_TARGET_DATASET
* When using stg, it materializes in the dataset defined in DBT_BIGQUERY_STAGING_DATASET, or defaults to DBT_BIGQUERY_TARGET_DATASET
* When using staging, it materializes in the dataset defined in DBT_BIGQUERY_STAGING_DATASET, or defaults to DBT_BIGQUERY_TARGET_DATASET
***

## Question 5: Taxi Quarterly Revenue Growth

1. Create a new model ```fct_taxi_trips_quarterly_revenue.sql```
2. Compute the Quarterly Revenues for each year for based on ```total_amount```
3. Compute the Quarterly YoY (Year-over-Year) revenue growth
   
* e.g.: In 2020/Q1, Green Taxi had -12.34% revenue growth compared to 2019/Q1
* e.g.: In 2020/Q4, Yellow Taxi had +34.56% revenue growth compared to 2019/Q4

Considering the YoY Growth in 2020, which were the yearly quarters with the best (or less worse) and worst results for green, and yellow

**Answer -> green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2}**

![Question 5](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/04-analytics-engineering/images/Qns%205.jpg)

```fct_taxi_trips_quarterly_revenue.sql```

```
{{
    config(
        materialized='table'
    )
}}

with trips_qtr_data as (
    select * from {{ ref('fact_trips') }}
),
rev_year_quarter as (
    select 
    -- Revenue grouping
    service_type,
    extract(quarter from pickup_datetime) as revenue_quarter,
    extract(year from pickup_datetime) as revenue_year,
 
    -- Revenue calculation 
    sum(total_amount) as revenue_year_quarter

    from trips_qtr_data
    where extract(year from pickup_datetime) in (2019,2020)
    group by 1,2,3 
    order by 1,2,3 desc
),
rev_yoy as (
    select
        service_type,
        revenue_quarter,
        revenue_year,
        revenue_year_quarter,
        LAG(revenue_year_quarter, 1) OVER
            (PARTITION BY service_type, revenue_quarter ORDER BY revenue_year) AS prev_year_rev
    from rev_year_quarter
),
yoy_calculated as (
    select
        service_type,
        revenue_quarter,
        revenue_year,
        revenue_year_quarter,
        prev_year_rev,
        (revenue_year_quarter - prev_year_rev) / prev_year_rev * 100 as yoy_growth
    from rev_yoy
    where revenue_year = 2020 -- Focus only on 2020 YoY growth
),
yoy_ranking as (
    select
        service_type,
        revenue_quarter,
        yoy_growth,
        -- Identify the best (max YoY growth) and worst (min YoY growth) quarters
        CASE 
            WHEN yoy_growth = (SELECT MAX(yoy_growth) FROM yoy_calculated y2 WHERE y2.service_type = y1.service_type) 
            THEN 'Best' 
        END as best_quarter,
        CASE 
            WHEN yoy_growth = (SELECT MIN(yoy_growth) FROM yoy_calculated y2 WHERE y2.service_type = y1.service_type) 
            THEN 'Worst' 
        END as worst_quarter
    from yoy_calculated y1
)

select * from yoy_ranking
order by service_type, yoy_growth desc
```

## Question 6: P97/P95/P90 Taxi Monthly Fare

1. Create a new model ```fct_taxi_trips_monthly_fare_p95.sql```
2. Filter out invalid entries (```fare_amount > 0```, ```trip_distance > 0```, and ```payment_type_description in ('Cash', 'Credit Card')```)
3. Compute the continous percentile of fare_amount partitioning by service_type, year and and month

Now, what are the values of ```p97```, ```p95```, ```p90``` for Green Taxi and Yellow Taxi, in April 2020?

**Answer -> green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}**

![Question 6](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/04-analytics-engineering/images/Qns%206.jpg)

```fct_taxi_trips_monthly_fare_p95.sql```

```
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
```

## Question 7: Top #Nth longest P90 travel time Location for FHV

Prerequisites:

* Create a staging model for FHV Data (2019), and DO NOT add a deduplication step, just filter out the entries where ```where dispatching_base_num is not null```
* Create a core model for FHV Data (```dim_fhv_trips.sql```) joining with ```dim_zones```. Similar to what has been done [here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/taxi_rides_ny/models/core/fact_trips.sql)
* Add some new dimensions ```year``` (e.g.: 2019) and ```month``` (e.g.: 1, 2, ..., 12), based on ```pickup_datetime```, to the core model to facilitate filtering for your queries

Now...

1. Create a new model ```fct_fhv_monthly_zone_traveltime_p90.sql```
2. For each record in ```dim_fhv_trips.sql```, compute the [timestamp_diff](https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions#timestamp_diff) in seconds between dropoff_datetime and pickup_datetime - we'll call it ```trip_duration``` for this exercise
3. Compute the continous ```p90``` of ```trip_duration partitioning``` by year, month, pickup_location_id, and dropoff_location_id

For the Trips that respectively started from ```Newark Airport```, ```SoHo```, and ```Yorkville East```, in November 2019, what are dropoff_zones with the 2nd longest p90 trip_duration ?

**Answer -> LaGuardia Airport, Chinatown, Garment District**

![Question 7](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/04-analytics-engineering/images/Qns%207.jpg)

```Staging model for FHV Data (2019): stg_fhv_tripdata.sql```

```
{{
    config(
        materialized='view'
    )
}}

with fhvdata as 
(
  select * from {{ source('staging', 'fhv_tripdata') }}
)

select
    -- identifiers
    {{ dbt_utils.generate_surrogate_key(['dispatching_base_num', 'pickup_datetime']) }} as tripid,
    dispatching_base_num,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    {{ dbt.safe_cast("pulocationid", api.Column.translate_type("integer")) }} as pickup_location_id,
    {{ dbt.safe_cast("dolocationid", api.Column.translate_type("integer")) }} as dropoff_location_id,
    {{ dbt.safe_cast("sr_flag", api.Column.translate_type("integer")) }} as sr_flag,
    affiliated_base_number
from fhvdata
where dispatching_base_num is not null
```

```Core Model for FHV Data (joined with dim_zones): dim_fhv_trips.sql```

```
{{
    config(
        materialized='table'
    )
}}

with fhv_data as (
    select *
    from {{ ref("stg_fhv_tripdata") }}
),
dim_zones as (
    select * from {{ ref("dim_zones") }}
    where borough != 'Unknown'
)

select 
    fhv_data.tripid,
    fhv_data.dispatching_base_num,
    extract(year from fhv_data.pickup_datetime) as fhv_year,
    extract(month from fhv_data.pickup_datetime) as fhv_month,
    fhv_data.pickup_datetime, 
    fhv_data.dropoff_datetime, 
    fhv_data.pickup_location_id,
    fhv_data.dropoff_location_id,
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,
    fhv_data.sr_flag,
    fhv_data.affiliated_base_number
from fhv_data
inner join dim_zones as pickup_zone
on fhv_data.pickup_location_id = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on fhv_data.dropoff_location_id = dropoff_zone.locationid
```

```New Model: fct_fhv_monthly_zone_traveltime_p90.sql```

```
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
```
>>>>>>> f9af180a83343be3183dec094afdd2b5681f1fe2
