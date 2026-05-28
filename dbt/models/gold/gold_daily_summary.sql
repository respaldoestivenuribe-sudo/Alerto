{{ 
    config(
        materialized='incremental',
        unique_key='date_local',
        on_schema_change='append_new_columns'
    ) 
}}

with daily as (

    select
        date_trunc('day', time_local)::date              as date_local,

        sum(precipitation_mm)::numeric(8,2)              as total_precipitation_mm,
        max(precipitation_mm)::numeric(8,2)              as max_hourly_precipitation_mm,
        avg(precipitation_mm)::numeric(8,2)              as avg_hourly_precipitation_mm,

        avg(humidity_pct)::numeric(5,2)                  as avg_humidity_pct,
        avg(windspeed_kmh)::numeric(6,2)                 as avg_windspeed_kmh,

        count(*)                                          as hours_recorded

    from {{ ref('silver_weather_hourly') }}

    {% if is_incremental() %}
        -- Reprocesamos solo el día actual (puede tener datos nuevos)
        -- y cualquier día más reciente
        where date_trunc('day', time_local)::date >= (
            select coalesce(max(date_local), '1900-01-01'::date) from {{ this }}
        )
    {% endif %}

    group by 1

),

final as (

    select
        *,
        current_timestamp as dbt_loaded_at
    from daily

)

select * from final