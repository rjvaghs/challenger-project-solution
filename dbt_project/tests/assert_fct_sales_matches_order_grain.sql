with counts as (
    select
        (select count(*) from {{ ref('stg_orders') }}) as order_rows,
        (select count(*) from {{ ref('fct_sales') }}) as sales_rows
)

select
    order_rows,
    sales_rows
from counts
where order_rows <> sales_rows
