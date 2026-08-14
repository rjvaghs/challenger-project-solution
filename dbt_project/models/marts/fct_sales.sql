with orders as (
    select *
    from {{ ref('stg_orders') }}
),

order_expenses as (
    select *
    from {{ ref('int_order_expenses') }}
),

joined as (
    select
        o.order_id,
        o.customer_id,
        cast(o.created_at as date) as order_date,
        o.channel,
        o.gross_revenue,
        coalesce(e.discount_amount, 0) as discount_amount,
        coalesce(e.refund_amount, 0) as refund_amount,
        coalesce(e.processing_fees, 0) as processing_fees,
        coalesce(e.shipping_cost, 0) as shipping_cost
    from orders as o
    left join order_expenses as e
        on o.order_id = e.order_id
)

select
    order_id,
    customer_id,
    order_date,
    channel,
    gross_revenue,
    discount_amount,
    refund_amount,
    processing_fees,
    shipping_cost,
    (gross_revenue - discount_amount - refund_amount - processing_fees - shipping_cost) as net_revenue
from joined
