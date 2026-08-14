# Key technical decisions and assumptions

## Technical decisions

### Ingestion

1. Pagination and CSV writing are shared; Orders and Expenses scripts only choose endpoint and output path. Extends the starter pattern without duplicating the extract loop.

2. CSV landing zone → DuckDB `raw` table for Orders and Expenses. One pipeline shape for both entities.

3. Each run overwrites landing CSVs and replaces raw tables. Incremental watermark/upsert design is documented for production, not implemented here.

4. Duplicates land as-is. Deduplication is deferred to dbt staging so raw remains an auditable extract.

5. Transient read failures retry with short backoff; missing pages fail immediately. Stand-in for real HTTP timeout / 5xx handling.

### dbt / Net Revenue

6. `stg_expenses` cleans long-form expenses; ephemeral `int_order_expenses` aggregates to order grain; `fct_sales` left-joins from `stg_orders` and computes Net Revenue.

7. Prevents expense fan-out from inflating Gross Revenue. Sales grain stays one row per `order_id`.

8. Named, reusable order-grain pivot without an extra physical table; inlined into `fct_sales` at compile time.

9. Null amounts coalesced in the pivot; orders with no expenses get expense columns coalesced to `0` so Net Revenue stays defined.

10. Handles duplicate and late-updated records for both `order_id` and `expense_id`.

## Assumptions

1. Mock API pagination (`has_more` / `next_page`) correctly describes the full result set.
2. Order and expense JSON schemas are stable enough for CSV headers from the first row.
3. Both ingest scripts run before `load_duckdb.py`; both landing CSVs are required to load.
4. Natural keys for upserts would be `order_id` (orders) and `expense_id` (expenses); `updated_at` is the watermark / “latest wins” field.
5. Multiple expense rows per order (and multiple types) are valid; they are summed by type at order grain in dbt.
6. Orphan expenses (no matching order) do not belong in `fct_sales`; orders drive the grain.
7. Net Revenue uses the challenge formula: Gross − Discounts − Refunds − Processing Fees − Shipping Cost.
8. Expanded Part 3 testing is in place: relationships, accepted expense types, Net Revenue formula, and order-grain integrity tests (see `dbt_project/tests/`).
