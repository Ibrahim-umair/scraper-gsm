from __future__ import annotations

import sqlite3
from pathlib import Path

from .parser import PhoneDetails


SCHEMA = """
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS phone_specs (
    phone_id INTEGER NOT NULL,
    spec_key TEXT NOT NULL,
    spec_value TEXT,
    PRIMARY KEY (phone_id, spec_key),
    FOREIGN KEY (phone_id) REFERENCES phones(id) ON DELETE CASCADE
);
"""


class PhoneStore:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert_phone(self, details: PhoneDetails) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO phones(name, url) VALUES(?, ?) ON CONFLICT(url) DO UPDATE SET name=excluded.name",
            (details.name, details.url),
        )
        cursor.execute("SELECT id FROM phones WHERE url = ?", (details.url,))
        phone_id = cursor.fetchone()[0]

        for key, value in details.specs.items():
            cursor.execute(
                """
                INSERT INTO phone_specs(phone_id, spec_key, spec_value)
                VALUES(?, ?, ?)
                ON CONFLICT(phone_id, spec_key) DO UPDATE SET spec_value=excluded.spec_value
                """,
                (phone_id, key, value),
            )

        self.conn.commit()

    def counts(self) -> tuple[int, int]:
        c1 = self.conn.execute("SELECT COUNT(*) FROM phones").fetchone()[0]
        c2 = self.conn.execute("SELECT COUNT(*) FROM phone_specs").fetchone()[0]
        return c1, c2
