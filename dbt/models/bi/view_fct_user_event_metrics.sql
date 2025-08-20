with source as (
    select * from {{ ref('fct_user_event_metrics') }}
),
final as (
    select
        user_id,
        email,
        region,
        first_seen_at,
        event_type,
        event_date,
        event_day_of_week,
        event_count,
        first_event_time,
        last_event_time
    from source
)

select * from final
