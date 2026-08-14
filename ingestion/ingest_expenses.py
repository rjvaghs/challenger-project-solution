"""
Expenses ingestion entrypoint (Part 1).

- Mirrors ingest_orders.py on purpose
- Only differences: endpoint="expenses" and output file raw_expenses.csv.
"""

from pathlib import Path

from ingestion.api_client import MockCommerceClient
from ingestion.common import fetch_all_pages, write_raw_csv

BASE_DIR = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = BASE_DIR / "warehouse"
OUTPUT_PATH = WAREHOUSE_DIR / "raw_expenses.csv"


def ingest_expenses():
    client = MockCommerceClient(endpoint="expenses")
    rows = fetch_all_pages(client)
    write_raw_csv(rows, OUTPUT_PATH, entity_name="expense")


if __name__ == "__main__":
    ingest_expenses()
