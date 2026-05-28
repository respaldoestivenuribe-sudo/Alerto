{{ 
    config(
        materialized='incremental',
        unique_key='time_local',
        on_schema_change='append_new_columns'
    ) 
}}

with source as (

    select
        time_local,
        time_utc,
        precipitation_mm

    from {{ ref('silver_weather_hourly') }}

    {% if is_incremental() %}
        -- Solo procesamos filas más nuevas que lo ya cargado
        where time_local > (select coalesce(max(time_local), '1900-01-01'::timestamptz) from {{ this }})
    {% endif %}

),

final as (

    select
        time_local,
        time_utc,
        precipitation_mm,
        current_timestamp as dbt_loaded_at

    from source

)

select * from final