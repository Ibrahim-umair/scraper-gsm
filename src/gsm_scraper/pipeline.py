from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from .client import PoliteClient
from .config import ScraperConfig
from .db import PhoneStore
from .parser import parse_brand_links, parse_phone_details, parse_phone_summaries


@dataclass(slots=True)
class ScrapeStats:
    brands: int = 0
    phone_pages: int = 0


def scrape(config: ScraperConfig, limit_brands: int | None = None, limit_phones_per_brand: int | None = None) -> ScrapeStats:
    stats = ScrapeStats()
    client = PoliteClient(config)
    store = PhoneStore(config.db_path)

    try:
        brands_html = client.get(urljoin(config.base_url + "/", config.brands_path))
        brand_links = parse_brand_links(brands_html, config.base_url)
        if limit_brands is not None:
            brand_links = brand_links[:limit_brands]

        for brand_url in brand_links:
            stats.brands += 1
            brand_html = client.get(brand_url)
            phone_links = parse_phone_summaries(brand_html, config.base_url)
            if limit_phones_per_brand is not None:
                phone_links = phone_links[:limit_phones_per_brand]

            for phone in phone_links:
                phone_html = client.get(phone.url)
                details = parse_phone_details(phone_html, phone.name, phone.url)
                if details.specs:
                    store.upsert_phone(details)
                stats.phone_pages += 1

        return stats
    finally:
        client.close()
        store.close()
