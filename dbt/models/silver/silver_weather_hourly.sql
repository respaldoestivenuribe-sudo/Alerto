{{ 
    config(
        materialized='incremental',
        unique_key='time_local',
        on_schema_change='append_new_columns'
    ) 
}}

with source as (

    select * from {{ source('bronze', 'bronze_weather_hourly') }}

    {% if is_incremental() %}
        -- Solo procesamos filas con fetched_at más reciente que lo ya cargado
        where fetched_at > (select coalesce(max(fetched_at), '1900-01-01'::timestamptz) from {{ this }})
    {% endif %}

),

cleaned as (

    select
        time::timestamptz                              as time_local,
        (time at time zone 'America/Bogota') 
            at time zone 'UTC'                         as time_utc,
        fetched_at::timestamptz                        as fetched_at,

        coalesce(precipitation, 0)::numeric(6,2)       as precipitation_mm,
        coalesce(rain, 0)::numeric(6,2)                as rain_mm,
        coalesce(showers, 0)::numeric(6,2)             as showers_mm,

        relative_humidity::numeric(5,2)                as humidity_pct,
        cloudcover::numeric(5,2)                       as cloudcover_pct,
        windspeed_10m::numeric(6,2)                    as windspeed_kmh,

        current_timestamp                              as dbt_loaded_at

    from source

),

deduplicated as (

    select distinct on (time_local)
        *
    from cleaned
    order by time_local, fetched_at desc

)

select * from deduplicated