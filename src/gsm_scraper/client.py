from __future__ import annotations

import random
import time
from dataclasses import dataclass

import httpx

from .config import ScraperConfig


@dataclass(slots=True)
class PoliteClient:
    config: ScraperConfig

    def __post_init__(self) -> None:
        self._session = httpx.Client(timeout=self.config.timeout_seconds, follow_redirects=True)
        self._request_timestamps: list[float] = []

    def close(self) -> None:
        self._session.close()

    def _wait_for_rate_limit(self) -> None:
        now = time.time()
        cutoff = now - 60
        self._request_timestamps = [t for t in self._request_timestamps if t >= cutoff]

        if len(self._request_timestamps) >= self.config.requests_per_minute:
            sleep_for = 60 - (now - self._request_timestamps[0])
            if sleep_for > 0:
                time.sleep(sleep_for)

        jitter = random.uniform(self.config.min_delay_seconds, self.config.max_delay_seconds)
        time.sleep(jitter)

    def get(self, url: str) -> str:
        for attempt in range(1, self.config.max_retries + 1):
            self._wait_for_rate_limit()
            headers = {
                "User-Agent": self.config.random_user_agent(),
                "Accept-Language": "en-US,en;q=0.9",
            }

            response = self._session.get(url, headers=headers)
            self._request_timestamps.append(time.time())

            if response.status_code in (429, 503):
                backoff = 2 ** attempt + random.uniform(0.0, 1.0)
                time.sleep(backoff)
                continue

            response.raise_for_status()
            return response.text

        raise RuntimeError(f"Failed to fetch {url} after {self.config.max_retries} retries")
