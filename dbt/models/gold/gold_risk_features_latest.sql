{{ 
    config(
        materialized='table'
    ) 
}}

with latest_data as (

    -- El timestamp más reciente disponible en Silver hourly
    select max(time_local) as as_of_time
    from {{ ref('silver_weather_hourly') }}
    having max(time_local) is not null

),

windows as (

    -- Calculamos todas las ventanas de tiempo desde el momento "as_of_time"
    select
        l.as_of_time,

        -- Intensidad actual: precipitación de la última hora
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '1 hour'
              and time_local <= l.as_of_time
        ) as precipitation_1h,

        -- Acumulada 3h
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '3 hours'
              and time_local <= l.as_of_time
        ) as precipitation_3h,

        -- Acumulada 6h
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '6 hours'
              and time_local <= l.as_of_time
        ) as precipitation_6h,

        -- Acumulada 24h
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '24 hours'
              and time_local <= l.as_of_time
        ) as precipitation_24h,

        -- Acumulada 72h (proxy saturación del suelo)
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '72 hours'
              and time_local <= l.as_of_time
        ) as precipitation_72h,

        -- Humedad promedio últimas 6h
        (
            select avg(humidity_pct)
            from {{ ref('silver_weather_hourly') }}
            where time_local > l.as_of_time - interval '6 hours'
              and time_local <= l.as_of_time
              and humidity_pct is not null
        ) as humidity_avg_6h

    from latest_data l

),

trend_calc as (

    -- Para la tendencia: comparamos lluvia última hora vs hora anterior
    select
        w.*,

        -- Precipitación de hace 1-2 horas (la "hora anterior")
        (
            select coalesce(sum(precipitation_mm), 0)
            from {{ ref('silver_weather_hourly') }}
            where time_local > w.as_of_time - interval '2 hours'
              and time_local <= w.as_of_time - interval '1 hour'
        ) as precipitation_prev_1h

    from windows w

),

final as (

    select
        as_of_time,

        -- Métricas para el motor difuso
        precipitation_1h::numeric(8,2)        as precipitation_1h,
        precipitation_3h::numeric(8,2)        as precipitation_3h,
        precipitation_6h::numeric(8,2)        as precipitation_6h,
        precipitation_24h::numeric(8,2)       as precipitation_24h,
        precipitation_72h::numeric(8,2)       as precipitation_72h,
        humidity_avg_6h::numeric(5,2)         as humidity_avg_6h,

        -- Intensidad = precipitación última hora (es lo mismo conceptualmente)
        precipitation_1h::numeric(8,2)        as intensity_mm_h,

        -- Tendencia: clasificación textual basada en diferencia
        case
            when precipitation_1h > precipitation_prev_1h * 1.2 then 'subiendo'
            when precipitation_1h < precipitation_prev_1h * 0.8 then 'bajando'
            else 'estable'
        end                                    as trend_1h,

        -- Diferencia numérica para que el backend pueda usarla si quiere
        (precipitation_1h - precipitation_prev_1h)::numeric(8,2)  as trend_delta,

        -- Auditoría
        current_timestamp                      as computed_at

    from trend_calc

)

select * from final