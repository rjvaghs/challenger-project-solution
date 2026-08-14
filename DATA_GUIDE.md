# Synthetic Challenge Data

All data in this package is fictional and created solely for the Data Engineer Challenger.

## Mock endpoints

The folders simulate paginated API responses:

- `mock_api/orders/page_1.json`, `page_2.json`, ...
- `mock_api/expenses/page_1.json`, `page_2.json`, ...

Each response has:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 15,
    "total_pages": 3,
    "has_more": true,
    "next_page": 2
  }
}
```

## Orders fields

- `order_id`
- `customer_id`
- `created_at`
- `updated_at`
- `product_id`
- `product_name`
- `channel`
- `gross_revenue`
- `currency`

## Expenses fields

- `expense_id`
- `order_id`
- `expense_type`
- `amount`
- `created_at`
- `updated_at`

Possible `expense_type` values:

- `discount`
- `refund`
- `processing_fee`
- `shipping_cost`

The dataset may contain duplicates, late-arriving updates, multiple expense rows for one order, null values, and orders with no associated expense records.

For the exercise:

`Net Revenue = Gross Revenue - Discounts - Refunds - Processing Fees - Shipping Cost`

Treat null expense amounts sensibly.
