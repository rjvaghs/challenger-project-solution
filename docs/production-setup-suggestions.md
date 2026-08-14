# Production setup

Brief suggestions for running this pipeline beyond the local challenge setup.

## Orchestration

Use **Airflow** to schedule and orchestrate the full path: API ingest (orders and expenses) → load to the warehouse → `dbt run` → `dbt test`. Airflow should own retries, alerting, and clear task dependencies so a failed ingest does not silently continue into dbt.

## Landing and archival

In production, do not rely on a single local overwrite CSV. API ingestion should write extract files to **SFTP** for on-premise environments, or to **object storage** (such as S3) in the cloud.

Treat landing files as immutable extracts. After a successful load, move or copy them into an archive area; keep failed files separate so they can be replayed. Retention can be handled with lifecycle policies (cloud) or scheduled cleanup (SFTP).

## File naming as metadata

Create archival and recovery metadata **in the Python ingest script** and put it in the **CSV file name**. A consistent naming convention matters more than a fixed local name like `raw_orders.csv`.

Include at least: entity (orders/expenses), extract mode (full vs incremental), time window or watermark, Airflow run id, attempt number, and generation timestamp (UTC). That supports archival partitioning, idempotent loads (skip already processed run ids), and failure recovery without guessing which file belonged to which run.

## dbt staging materialization

Locally, staging models are views. In production, materialize staging as **tables** so cleaned data is persisted, easier to debug, and cheaper for repeated downstream reads and tests. Marts should remain tables; intermediate models can stay ephemeral if they are only used by one mart.

## Load pattern

Prefer upserts into raw on natural keys (`order_id`, `expense_id`) over dropping and recreating tables each run, especially once incremental extracts and named landing files are in place.

## Quality and operations

Keep `dbt test` in the Airflow DAG after `dbt run`. Add monitoring for freshness, row counts per file, and API failure rates. Store secrets outside code and use a real HTTP client with retries and backoff.
