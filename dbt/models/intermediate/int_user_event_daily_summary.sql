with source as (
    select * from {{ ref('stg_game_events') }}
),
final as (
    select
        user_id,
        email,
        event_type,
        date_trunc(event_time, day) as event_date,
        format_timestamp('%A', event_time) as event_day_of_week,
        count(*) as event_count,
        min(event_time) as first_event_time,
        max(event_time) as last_event_time
    from source
    group by
        user_id,
        email,
        event_type,
        event_date,
        event_day_of_week
)

select * from final
