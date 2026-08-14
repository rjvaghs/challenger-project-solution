with source as (
    select *
    from {{ source('raw', 'expenses') }}
),

typed as (
    select
        cast(expense_id as varchar) as expense_id,
        cast(order_id as varchar) as order_id,
        cast(expense_type as varchar) as expense_type,
        cast(amount as decimal(18, 2)) as amount,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from source
),

deduplicated as (
    select *
    from typed
    qualify row_number() over (
        partition by expense_id
        order by updated_at desc
    ) = 1
)

select * from deduplicated
