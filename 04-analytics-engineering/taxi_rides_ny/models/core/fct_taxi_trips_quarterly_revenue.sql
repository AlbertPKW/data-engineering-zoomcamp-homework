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
)

select
    service_type,
    revenue_quarter,
    revenue_year,
    revenue_year_quarter,
    prev_year_rev,
    (revenue_year_quarter - prev_year_rev) / prev_year_rev * 100 as yoy_growth
from rev_yoy
order by 1,2,3 desc

