"""
Load landing-zone CSVs into the local DuckDB raw schema.

Part 1 extension:
- Previously only loaded raw.orders.
- Now also loads raw.expenses using the same full-replace pattern.
"""

from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = BASE_DIR / "warehouse"
DB_PATH = WAREHOUSE_DIR / "challenge.duckdb"

RAW_TABLES = {
    "orders": WAREHOUSE_DIR / "raw_orders.csv",
    "expenses": WAREHOUSE_DIR / "raw_expenses.csv",
}


def load_csv_as_table(con: duckdb.DuckDBPyConnection, table_name: str, csv_path: Path) -> None:
    """Drop and recreate raw.<table> from the CSV (full refresh)."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path.as_posix()} does not exist. "
            f"Run the matching ingest script first (e.g. python -m ingestion.ingest_{table_name})."
        )

    # Incremental note: currently we replace the whole table each run.
    # Production would MERGE/upsert on natural keys (order_id / expense_id) instead.
    con.execute(f"drop table if exists raw.{table_name}")
    con.execute(
        f"""
        create table raw.{table_name} as
        select * from read_csv_auto('{csv_path.as_posix()}', header=true)
        """
    )
    print(f"Loaded raw.{table_name} into {DB_PATH}")


def main():
    con = duckdb.connect(str(DB_PATH))
    con.execute("create schema if not exists raw")

    for table_name, csv_path in RAW_TABLES.items():
        load_csv_as_table(con, table_name, csv_path)

    con.close()


if __name__ == "__main__":
    main()
