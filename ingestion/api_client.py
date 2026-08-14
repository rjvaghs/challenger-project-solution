"""
- Previously supported Orders only (NotImplementedError for anything else).
- Part 1 change: endpoints under mock_api/ are allowed (orders + expenses).
- Includes a small retry so transient read failures are handled cleanly.
"""

from pathlib import Path
import json
import time

BASE_DIR = Path(__file__).resolve().parents[1]
MOCK_API_DIR = BASE_DIR / "mock_api"

SUPPORTED_ENDPOINTS = {"orders", "expenses"}


class MockCommerceClient:

    def __init__(self, endpoint="orders", max_retries=3, retry_delay_seconds=0.1):
        if endpoint not in SUPPORTED_ENDPOINTS:
            raise ValueError(
                f"Unsupported endpoint '{endpoint}'. "
                f"Expected one of: {sorted(SUPPORTED_ENDPOINTS)}"
            )
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def get_page(self, page=1):
        """
        Return one API page as a dict with keys: data, pagination.

        Failed requests: retries transient read failures a few times, then throws
        a clear error. In a real API this would wrap HTTP timeouts similarly.
        """
        path = MOCK_API_DIR / self.endpoint / f"page_{page}.json"
        if not path.exists():
            # Missing page is a hard failure.
            raise FileNotFoundError(f"Mock API page not found: {path}")

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                # Brief backoff before the next attempt.
                time.sleep(self.retry_delay_seconds * attempt)

        raise RuntimeError(
            f"Failed to read {path} after {self.max_retries} attempts: {last_error}"
        ) from last_error
