{{ 
    config(
        materialized='incremental',
        unique_key='bronze_id',
        on_schema_change='append_new_columns'
    ) 
}}

with source as (

    select * from {{ source('bronze', 'bronze_weather_current') }}

    {% if is_incremental() %}
        where id > (select coalesce(max(bronze_id), 0) from {{ this }})
    {% endif %}

), cleaned as (

    select
        id                                             as bronze_id,
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

),deduplicated as (

    select distinct on (bronze_id)
        *
    from cleaned
    order by bronze_id, fetched_at desc

)

select * from deduplicated