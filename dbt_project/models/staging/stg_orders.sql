with source as (
    select *
    from {{ source('raw', 'orders') }}
),

typed as (
    select
        cast(order_id as varchar) as order_id,
        cast(customer_id as varchar) as customer_id,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        cast(product_id as varchar) as product_id,
        cast(product_name as varchar) as product_name,
        cast(channel as varchar) as channel,
        cast(gross_revenue as decimal(18,2)) as gross_revenue,
        cast(currency as varchar) as currency
    from source
),

deduplicated as (
    select *
    from typed
    qualify row_number() over (
        partition by order_id
        order by updated_at desc
    ) = 1
)

select * from deduplicated
