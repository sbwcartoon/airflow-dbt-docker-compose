with source as (
    select * from {{ source('raw', 'game_events') }}
),
cleaned as (
    select
        event_id,
        user_id,
        email,
        event_type,
        cast(event_at as timestamp) as event_time,
        cast(loaded_at as timestamp) as loaded_at
    from source
    where email is not null
),
final as (
    select
        user_id,
        email,
        event_type,
        event_time,
        loaded_at
    from cleaned
)

select * from final