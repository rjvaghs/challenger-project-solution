"""
Shared ingestion helpers used by Orders and Expenses.

Why a shared module:
- Pagination + CSV landing logic is identical for both endpoints.
- Endpoint scripts stay thin wrappers so the pattern stays easy to follow.
- Avoids copy-paste when another endpoint is added later.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ingestion.api_client import MockCommerceClient


def fetch_all_pages(client: MockCommerceClient) -> list[dict]:
    """
    Walk every page until pagination.has_more is false.

    Pagination uses the mock API contract (has_more + next_page), same as the
    original Orders script.

    Duplicates: every row returned by the API is kept in the raw layer.
    Deduping belongs in dbt staging. 
    """
    rows: list[dict] = []
    page = 1

    while True:
        response = client.get_page(page)
        rows.extend(response["data"])

        pagination = response["pagination"]
        if not pagination["has_more"]:
            break

        page = pagination["next_page"]

    return rows


def write_raw_csv(rows: list[dict], output_path: Path, entity_name: str) -> None:
    """
    Full-refresh write of the landing-zone CSV.

    Incremental ingestion (current vs production):
    Currently, we overwrite the CSV each run (full replace), which is
    fine for this small synthetic dataset and matches the starter Orders behaviour.

    In production we would typically:
    1. Track a watermark (e.g. max(updated_at) already loaded).
    2. Request only records newer than that watermark.
    3. Append or upsert into the raw table instead of dropping it.
    Raw still stores history; staging/marts decide the current business view.
    """
    if not rows:
        raise RuntimeError(f"No {entity_name} rows were returned.")

    output_path.parent.mkdir(exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} raw {entity_name} rows to {output_path}")
