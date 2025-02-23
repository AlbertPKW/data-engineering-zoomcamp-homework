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