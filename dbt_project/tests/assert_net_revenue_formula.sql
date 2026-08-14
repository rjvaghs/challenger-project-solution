with expected as (
    select
        o.order_id,
        (
            o.gross_revenue
            - coalesce(sum(case when e.expense_type = 'discount' then coalesce(e.amount, 0) end), 0)
            - coalesce(sum(case when e.expense_type = 'refund' then coalesce(e.amount, 0) end), 0)
            - coalesce(sum(case when e.expense_type = 'processing_fee' then coalesce(e.amount, 0) end), 0)
            - coalesce(sum(case when e.expense_type = 'shipping_cost' then coalesce(e.amount, 0) end), 0)
        ) as expected_net_revenue
    from {{ ref('stg_orders') }} as o
    left join {{ ref('stg_expenses') }} as e
        on o.order_id = e.order_id
    group by o.order_id, o.gross_revenue
)

select
    f.order_id,
    f.net_revenue as fct_net_revenue,
    e.expected_net_revenue
from {{ ref('fct_sales') }} as f
inner join expected as e
    on f.order_id = e.order_id
where f.net_revenue <> e.expected_net_revenue
