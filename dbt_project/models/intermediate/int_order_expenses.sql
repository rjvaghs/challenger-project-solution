with expenses as (
    select
        order_id,
        expense_type,
        coalesce(amount, 0) as amount
    from {{ ref('stg_expenses') }}
)

select
    order_id,
    sum(case when expense_type = 'discount' then amount else 0 end) as discount_amount,
    sum(case when expense_type = 'refund' then amount else 0 end) as refund_amount,
    sum(case when expense_type = 'processing_fee' then amount else 0 end) as processing_fees,
    sum(case when expense_type = 'shipping_cost' then amount else 0 end) as shipping_cost
from expenses
group by order_id
