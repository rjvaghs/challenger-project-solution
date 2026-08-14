# Data Engineer Challenger - Starter Project

Solution for the Data Engineer Challenger: Python ingestion for Orders and Expenses, dbt models for Gross and Net Revenue, and data-quality tests.

All data is synthetic. No My Derma Dream production data is included.

## What this project does

- Ingests paginated **Orders** and **Expenses** from a mock API into landing CSVs, then loads DuckDB `raw.orders` and `raw.expenses`
- Builds dbt staging, an order-grain expense intermediate, and `fct_sales` with Gross Revenue, expense components, and Net Revenue
- Runs dbt tests for keys, relationships, expense types, order grain, and Net Revenue reconciliation against staging

**Net Revenue** = Gross Revenue − Discounts − Refunds − Processing Fees − Shipping Cost

## Project structure

```text
.
├── ingestion/
│   ├── api_client.py
│   ├── common.py
│   ├── ingest_orders.py
│   └── ingest_expenses.py
├── mock_api/
│   ├── orders/
│   └── expenses/
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── tests/
├── scripts/
│   └── load_duckdb.py
├── warehouse/
├── solution/
│   ├── challenge-qa.md
│   ├── technical-decisions-and-assumptions.md
│   └── production-setup-suggestions.md
├── requirements.txt
└── README.md
```



## Local setup

Python 3.10+ recommended.

### 1. Create a virtual environment

Mac/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

If scripts are still blocked, use Command Prompt (`.venv\Scripts\activate.bat`) or run `.venv\Scripts\python.exe` without activating.



### 2. Install dependencies

```bash
pip install -r requirements.txt
```



### 3. Ingest Orders and Expenses

From the project root:

```bash
python -m ingestion.ingest_orders
python -m ingestion.ingest_expenses
```

This creates:

```text
warehouse/raw_orders.csv
warehouse/raw_expenses.csv
```

Shared pagination and CSV helpers live in `ingestion/common.py`. The client supports both mock endpoints and retries transient read failures.

### 4. Load raw tables into DuckDB

```bash
python scripts/load_duckdb.py
```

Creates `warehouse/challenge.duckdb` with `raw.orders` and `raw.expenses` (full replace each run).

### 5. Run dbt

```bash
cd dbt_project
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Builds:

- `stg_orders` - cleaned, deduplicated orders
- `stg_expenses` - cleaned, deduplicated expenses
- `int_order_expenses` - ephemeral; expense amounts pivoted to order grain
- `fct_sales` - one row per `order_id` with Gross Revenue, expense components, and Net Revenue

`dbt test` covers identifier uniqueness, expense→order relationships, accepted expense types, Net Revenue reconciliation to staging, and order-grain integrity.

Expenses are aggregated to order grain **before** joining to orders so Gross Revenue is not inflated by multiple expense rows.

## Documentation

- `solution/challenge-qa.md` — answers to the challenge README questions
- `solution/technical-decisions-and-assumptions.md` — key decisions and assumptions
- `solution/production-setup-suggestions.md` — production ideas



## Mock API

`mock_api/orders` and `mock_api/expenses` simulate paginated responses:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 15,
    "total_pages": 3,
    "has_more": true,
    "next_page": 2
  }
}
```

See `DATA_GUIDE.md` for field lists and expense types.

Do not include confidential employer information, credentials or API keys in your submission.