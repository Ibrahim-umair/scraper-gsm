from __future__ import annotations

import argparse

from .config import load_config
from .pipeline import scrape
from .db import PhoneStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Polite GSM Arena scraper for learning")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config")
    parser.add_argument("--limit-brands", type=int, default=2, help="Limit brand pages (default: 2)")
    parser.add_argument(
        "--limit-phones-per-brand",
        type=int,
        default=5,
        help="Limit phone pages per brand (default: 5)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    stats = scrape(
        config,
        limit_brands=args.limit_brands,
        limit_phones_per_brand=args.limit_phones_per_brand,
    )

    store = PhoneStore(config.db_path)
    phones, specs = store.counts()
    store.close()

    print(f"Scraped brands: {stats.brands}")
    print(f"Visited phone pages: {stats.phone_pages}")
    print(f"Stored phones: {phones}")
    print(f"Stored specs rows: {specs}")


if __name__ == "__main__":
    main()
