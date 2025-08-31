from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from contextlib import contextmanager
import psycopg2
from psycopg2 import OperationalError, DatabaseError, sql
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, execute_values
import time
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger("db")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    _ch = logging.StreamHandler()
    _ch.setFormatter(logging.Formatter("[%(levelname)s] db: %(message)s"))
    logger.addHandler(_ch)

PGDATABASE = os.getenv("PGDATABASE", ":) Your DB Name Here :)")
PGUSER = os.getenv("PGUSER", ") Your DB User Name Here :)")
PGPASSWORD = os.getenv("PGPASSWORD", ") Your Password Here :)")
PGHOST = os.getenv("PGHOST", ":) Your DC Host Here :)")
PGPORT = int(os.getenv("PGPORT", "5432")) #5432 (default, but you can write your db port)

PGSSLMODE = os.getenv("PGSSLMODE", ":) Your DC Mode Here :)")

PG_MINCONN = int(os.getenv("PG_MINCONN", "1"))
PG_MAXCONN = int(os.getenv("PG_MAXCONN", "5"))

_POOL: Optional[SimpleConnectionPool] = None

def _ensure_pool() -> SimpleConnectionPool:
    global _POOL
    if _POOL is not None:
        return _POOL

    dsn = (
        f"host={PGHOST} port={PGPORT} dbname={PGDATABASE} "
        f"user={PGUSER} password={PGPASSWORD} sslmode={PGSSLMODE}"
    )
    try:
        _POOL = SimpleConnectionPool(
            PG_MINCONN, PG_MAXCONN, dsn=dsn, cursor_factory=RealDictCursor
        )
        logger.info("Database connection successfully initialized!")
    except Exception as e:
        logger.error("Failed to initialize connection pool: %s!", e)
        raise
    return _POOL

@contextmanager
def get_conn():
    pool = _ensure_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn is not None:
            pool.putconn(conn)

def _with_retry(func, attempts: int = 3, base_delay: float = 0.5):
    last_exc = None
    for i in range(attempts):
        try:
            return func()
        except OperationalError as e:
            last_exc = e
            delay = base_delay * (2 ** i)
            logger.warning("OperationalError, retrying in %.1fs (%d/%d): %s",delay, i + 1, attempts, e)
            time.sleep(delay)
        except DatabaseError as e:
            logger.error("DatabaseError (no retry): %s", e)
            raise
    assert last_exc is not None
    raise last_exc

def init_db() -> None:
    def _do():
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    log_type VARCHAR(32) NOT NULL,
                    log_message TEXT NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(log_type);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);")
            conn.commit()
    _with_retry(_do)

def insert_log_row(log_type: str, log_message: str, hostname: str, created_at) -> Dict[str, Any]:
    def _do():
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO logs (log_type, log_message, hostname, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id, log_type, log_message, hostname, created_at;
                """,
                (log_type, log_message, hostname, created_at)
            )
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else {}
    return _with_retry(_do)

def insert_logs_bulk(rows: Sequence[Tuple[str, str, str, Any]]) -> int:
    if not rows:
        return 0

    def _do():
        with get_conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO logs (log_type, log_message, hostname, created_at)
                VALUES %s
                """,
                rows
            )
            affli = cur.rowcount or len(rows)
            conn.commit()
            return affli
    return _with_retry(_do)

def fetch_logs(log_types: Optional[Sequence[str]] = None, limit: int = 500) -> List[Dict[str, Any]]:
    def _do():
        with get_conn() as conn, conn.cursor() as cur:
            if log_types:
                cur.execute(
                    """
                    SELECT id, log_type, log_message, hostname, created_at
                    FROM logs
                    WHERE log_type = ANY(%s)
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (list(log_types), limit)
                )
            else:
                cur.execute(
                    """
                    SELECT id, log_type, log_message, hostname, created_at
                    FROM logs
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
            rows = cur.fetchall() or []
            return [dict(r) for r in rows]
    return _with_retry(_do)

def healthcheck() -> Tuple[bool, str]:
    try:
        def _do():
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                conn.commit()
        _with_retry(_do, attempts=2)
        return True, "Database connection is perfectly healthy!"
    except Exception as e:
        return False, f"Database connection failed: {e} !"

def reset_log_table() -> None:
    def _do():
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE logs RESTART IDENTITY;")
            conn.commit()
            logger.info("Log table reset and ID counter restarted.")
    _with_retry(_do)