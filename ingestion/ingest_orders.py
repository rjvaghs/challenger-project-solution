"""
Orders ingestion entrypoint.

- Behaviour is unchanged: paginate Orders to warehouse/raw_orders.csv.
- Logic now lives in common.py so Expenses can reuse the same pattern.
"""

from pathlib import Path

from ingestion.api_client import MockCommerceClient
from ingestion.common import fetch_all_pages, write_raw_csv

BASE_DIR = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = BASE_DIR / "warehouse"
OUTPUT_PATH = WAREHOUSE_DIR / "raw_orders.csv"


def ingest_orders():
    client = MockCommerceClient(endpoint="orders")
    rows = fetch_all_pages(client)
    write_raw_csv(rows, OUTPUT_PATH, entity_name="order")


if __name__ == "__main__":
    ingest_orders()
