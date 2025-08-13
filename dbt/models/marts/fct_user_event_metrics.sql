{{ config(unique_key=['user_id', 'email', 'event_type', 'event_date', 'event_day_of_week']) }}

with source as (
    select * from {{ ref('int_user_event_daily_summary') }}
),
dim_users as (
    select * from {{ ref('dim_users') }}
),
final as (
    select
        s.user_id,
        s.email,
        du.region,
        du.first_seen_at,
        s.event_type,
        s.event_date,
        s.event_day_of_week,
        s.event_count,
        s.first_event_time,
        s.last_event_time
    from source s
    inner join dim_users du
        on s.user_id = du.user_id
)

select * from final
