from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import yaml


DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


@dataclass(slots=True)
class ScraperConfig:
    base_url: str = "https://www.gsmarena.com"
    brands_path: str = "makers.php3"
    requests_per_minute: int = 20
    min_delay_seconds: float = 1.8
    max_delay_seconds: float = 4.0
    timeout_seconds: float = 25.0
    max_retries: int = 4
    db_path: str = "data/gsmarena.sqlite"
    user_agents: list[str] | None = None

    @property
    def ua_pool(self) -> list[str]:
        return self.user_agents or DEFAULT_USER_AGENTS

    def random_user_agent(self) -> str:
        return random.choice(self.ua_pool)



def load_config(path: str | Path = "config.yaml") -> ScraperConfig:
    config_path = Path(path)
    if not config_path.exists():
        return ScraperConfig()

    payload = yaml.safe_load(config_path.read_text()) or {}
    return ScraperConfig(**payload)
