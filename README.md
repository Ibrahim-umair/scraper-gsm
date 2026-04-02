# Smart (Polite) GSM Arena Scraper - Learning Project

This project is intentionally built for **learning how real-world scraping projects are structured**, not just grabbing HTML once.

## Why this is better than a simple scraper

A simple scraper gets blocked quickly because it:
- sends requests too fast,
- uses the same request fingerprint forever,
- has no retry strategy,
- crashes without storing progress.

This project includes:
- rate limiting + random jitter,
- rotating user agents,
- retry with exponential backoff for `429` / `503`,
- structured parsing,
- normalized storage in SQLite (`phones` + `phone_specs`),
- idempotent upserts so reruns are safe.

## Folder structure

- `src/gsm_scraper/client.py` — HTTP client with anti-block behavior.
- `src/gsm_scraper/parser.py` — parsing logic (brands, phone list, details).
- `src/gsm_scraper/db.py` — SQLite schema + upserts.
- `src/gsm_scraper/pipeline.py` — crawl orchestration.
- `src/gsm_scraper/main.py` — CLI entrypoint.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

```bash
cp config.example.yaml config.yaml
```

Tune these safely:
- `requests_per_minute` (keep low at first, e.g. 10–20)
- `min_delay_seconds` / `max_delay_seconds`
- user-agent list

## Run

Start very small while learning:

```bash
PYTHONPATH=src python -m gsm_scraper.main --limit-brands 1 --limit-phones-per-brand 2
```

Then inspect DB:

```bash
sqlite3 data/gsmarena.sqlite "select count(*) from phones;"
sqlite3 data/gsmarena.sqlite "select spec_key, spec_value from phone_specs limit 20;"
```

## How people build robust scrapers in practice

1. **Check legal/TOS/robots first**
   - Respect website terms and avoid prohibited access.
2. **Capture stable selectors**
   - Keep parser functions small so selector updates are easy.
3. **Design for retries and partial failure**
   - Network errors and occasional HTTP 429 are expected.
4. **Persist incrementally**
   - Save each record as soon as it is parsed.
5. **Measure and monitor**
   - Log pages fetched, retries, and parse failures.
6. **Evolve to queue/workers when scaling**
   - Start single-process; scale only after correctness.

## Suggested next steps for you

- Add logging to file + retry counters.
- Add a `scrape_jobs` table and mark each URL status (`queued`, `done`, `failed`).
- Store raw HTML snapshots for parser debugging.
- Add tests with saved fixture pages so parser changes are safe.
- Add proxy support (only if policy allows and you need it).

---

If you want, next I can help you add:
1) URL queue with resumable state, and
2) parser unit tests from real GSM Arena HTML snapshots.
