# Challenge Q&A

Answers to the README questions for this solution (ingestion + dbt Net Revenue).

## 1. What did you change and why?

The starter pipeline only ingested **Orders** and reported **Gross Revenue**. The business needed **Expenses** in the warehouse and **Net Revenue** on the sales model.

Functionally:

- **Ingestion** now pulls paginated Expenses the same way as Orders, lands them as raw CSV, and loads `raw.expenses` into DuckDB - so expense data is available for modelling without inventing a second pipeline shape.
- **dbt** adds cleaned expenses, aggregates them to order grain before joining, and extends `fct_sales` with discount, refund, processing fees, shipping cost, and Net Revenue - without changing the sales grain or inflating Gross Revenue when many expense rows exist for one order.

## 2. How does the new ingestion flow work?

Both Orders and Expenses follow the same path:

1. **Extract** - A client reads paginated mock API pages (`has_more` / `next_page`) until complete.
2. **Land** - All returned rows are written to a landing CSV under `warehouse/` (full overwrite each run).
3. **Load** - DuckDB recreates `raw.orders` and `raw.expenses` from those CSVs.

Shared helpers handle pagination and CSV writing; thin scripts choose the endpoint and output path. Raw keeps API output as-is (including duplicates); cleaning happens later in dbt staging.

## 3. How would you handle incremental ingestion?

**Today:** full extract and full replace (overwrite CSV, recreate raw tables). Fine for this small synthetic dataset and consistent with the starter Orders behaviour.

**In production:**

1. Persist a watermark per endpoint (typically `max(updated_at)` after a successful load).
2. Extract only records newer than that watermark (API filter).
3. Upsert into raw on natural keys (`order_id`, `expense_id`) instead of dropping the table.
4. Advance the watermark only after a successful load; keep staging “latest `updated_at` wins” so re-runs stay idempotent for metrics.

## 4. How does your solution prevent duplicate data from affecting the metrics?

- **Raw:** duplicates may land (faithful extract).
- **Staging:** `stg_orders` keeps one row per `order_id` (latest `updated_at`); `stg_expenses` keeps one row per `expense_id` (latest `updated_at`).
- **Before the sales join:** `int_order_expenses` aggregates expenses to **one row per `order_id`** (sums by expense type). That stops expense fan-out from multiplying Gross Revenue.
- **Mart:** `fct_sales` is driven from orders with a left join to that order-grain expense table, so each order contributes Gross Revenue once.

## 5. What is the grain of your final sales model?

**One row per `order_id`.**

That matches the starter `fct_sales` grain. Expense detail is rolled up to the order before joining, so the fact stays order-level.

## 6. How did you calculate Net Revenue?

Using the challenge definition:

**Net Revenue = Gross Revenue − Discounts − Refunds − Processing Fees − Shipping Cost**

In practice:

- Expense amounts are summed by `expense_type` at order grain.
- Null amounts are treated as `0`.
- Orders with no expenses get expense columns coalesced to `0`.
- `fct_sales` then applies the formula above.

## 7. What happens if the API fails?

The client **retries** transient read failures a few times with short backoff, then raises a clear error and stops that ingest run.

Missing pages (broken pagination) fail immediately without retry. The load step is not run successfully for a failed extract, so partial bad data is not silently promoted. In production, the same idea would wrap HTTP timeouts / 5xx, and watermarks would only move after a successful load.

## 8. What would you add or change before putting this into production?

- **Incremental ingestion** with watermarks and upserts (not full refresh).
- Stronger **API resilience**: retries with jitter or exponential backoff, rate limits, dead-letter / alerting, structured logging and run metrics.
- **Orchestration** (e.g. scheduled DAG) with clear dependencies: ingest to load to dbt to tests.
- Richer **data quality**: relationship tests (expenses > orders), accepted expense types, Net Revenue expression tests, anomaly checks on revenue vs expenses.
- **Secrets / config** outside code; real HTTP client instead of file mocks; environment-specific warehouses.
- **Observability**: freshness SLAs, row-count monitors, cost and runtime tracking.
- Clear ownership of **late-arriving updates** and how Net Revenue is restated when expenses change after order creation.
