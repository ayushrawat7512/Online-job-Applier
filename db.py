"""
Bahut simple SQLite based dedup store. Har job ka unique ID (link ka hash)
store hota hai jab wo ek baar Telegram pe bhej diya jaye - taaki dobara
same job notify na ho, chahe script kitni baar bhi chale.
"""
import sqlite3
import hashlib
import time
from contextlib import contextmanager

from config import DB_PATH


def _job_id(link: str) -> str:
    return hashlib.sha256(link.strip().encode("utf-8")).hexdigest()


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_jobs (
                job_id     TEXT PRIMARY KEY,
                source     TEXT NOT NULL,
                title      TEXT,
                company    TEXT,
                link       TEXT,
                sent_at    INTEGER
            )
            """
        )
        # Purana data automatically clean karne ke liye - 30 din se purana
        # data delete kar dete hai taaki DB file zyada bada na ho.
        cutoff = int(time.time()) - 30 * 24 * 3600
        conn.execute("DELETE FROM sent_jobs WHERE sent_at < ?", (cutoff,))


def already_sent(link: str) -> bool:
    jid = _job_id(link)
    with _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sent_jobs WHERE job_id = ?", (jid,)
        ).fetchone()
        return row is not None


def mark_sent(source: str, title: str, company: str, link: str):
    jid = _job_id(link)
    with _conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO sent_jobs
                (job_id, source, title, company, link, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (jid, source, title, company, link, int(time.time())),
        )
