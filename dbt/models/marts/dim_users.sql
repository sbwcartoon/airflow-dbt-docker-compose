with source as (
    select * from {{ ref('int_user_event_daily_summary') }}
),
cleaned as (
    select
        user_id,
        min(event_date) as first_seen_at
    from source
    group by user_id
),
final as (
    select
        user_id,
        'unknown' as region,
        first_seen_at
    from cleaned
)

select * from final