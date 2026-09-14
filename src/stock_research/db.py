"""DuckDB database manager for the stock research system.

Manages the research database at .notlocal/data/personal-investor/db/research.duckdb.
Provides schema creation, upsert helpers, and freshness tracking for all data sources.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import duckdb
except ImportError:
    raise ImportError(
        "duckdb is required for the stock research database. "
        "Install it with: pip install duckdb"
    )

# Default DB path relative to the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = str(_PROJECT_ROOT / ".notlocal" / "data" / "personal-investor" / "db" / "research.duckdb")


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_TABLES: dict[str, str] = {
    "company_fundamentals": """
        CREATE TABLE IF NOT EXISTS company_fundamentals (
            ticker                TEXT NOT NULL,
            period                TEXT NOT NULL,
            period_end            DATE,
            revenue               DOUBLE,
            revenue_yoy_growth    DOUBLE,
            gross_margin          DOUBLE,
            operating_margin      DOUBLE,
            net_income            DOUBLE,
            eps                   DOUBLE,
            operating_cash_flow   DOUBLE,
            capex                 DOUBLE,
            free_cash_flow        DOUBLE,
            cash                  DOUBLE,
            debt                  DOUBLE,
            shares_outstanding    DOUBLE,
            sbc                   DOUBLE,
            roe                   DOUBLE,
            roic                  DOUBLE,
            source                TEXT,
            updated_at            TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, period)
        )
    """,
    "earnings": """
        CREATE TABLE IF NOT EXISTS earnings (
            ticker                TEXT NOT NULL,
            fiscal_period         TEXT NOT NULL,
            announcement_date     DATE,
            revenue_actual        DOUBLE,
            revenue_estimate      DOUBLE,
            revenue_surprise_pct  DOUBLE,
            eps_actual            DOUBLE,
            eps_estimate          DOUBLE,
            eps_surprise_pct      DOUBLE,
            guidance              TEXT,
            guidance_change       TEXT,
            stock_return_1d       DOUBLE,
            stock_return_5d       DOUBLE,
            stock_return_20d      DOUBLE,
            source                TEXT,
            updated_at            TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, fiscal_period)
        )
    """,
    "prices": """
        CREATE TABLE IF NOT EXISTS prices (
            ticker         TEXT NOT NULL,
            date           DATE NOT NULL,
            open           DOUBLE,
            high           DOUBLE,
            low            DOUBLE,
            close          DOUBLE,
            adjusted_close DOUBLE,
            volume         BIGINT,
            source         TEXT,
            updated_at     TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, date)
        )
    """,
    "valuation": """
        CREATE TABLE IF NOT EXISTS valuation (
            ticker           TEXT NOT NULL,
            date             DATE NOT NULL,
            market_cap       DOUBLE,
            pe               DOUBLE,
            forward_pe       DOUBLE,
            ev_sales         DOUBLE,
            ev_ebitda        DOUBLE,
            price_sales      DOUBLE,
            fcf_yield        DOUBLE,
            enterprise_value DOUBLE,
            source           TEXT,
            updated_at       TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, date)
        )
    """,
    "sentiment_observations": """
        CREATE TABLE IF NOT EXISTS sentiment_observations (
            ticker              TEXT NOT NULL,
            date                DATE,
            source              TEXT,
            source_id           TEXT,
            author              TEXT,
            title               TEXT,
            snippet             TEXT,
            engagement_score    DOUBLE,
            sentiment_direction TEXT,
            sentiment_strength  DOUBLE,
            narrative_label     TEXT,
            bull_bear           TEXT,
            source_url          TEXT,
            updated_at          TIMESTAMP DEFAULT current_timestamp
        )
    """,
    "investor_claims": """
        CREATE TABLE IF NOT EXISTS investor_claims (
            claim_id             TEXT PRIMARY KEY,
            ticker               TEXT NOT NULL,
            date                 DATE,
            claim                TEXT,
            claim_type           TEXT,
            bull_bear            TEXT,
            source               TEXT,
            source_url           TEXT,
            evidence_text        TEXT,
            evidence_strength    TEXT,
            verification_status  TEXT,
            updated_at           TIMESTAMP DEFAULT current_timestamp
        )
    """,
    "research_snapshots": """
        CREATE TABLE IF NOT EXISTS research_snapshots (
            ticker         TEXT NOT NULL,
            snapshot_date  DATE NOT NULL,
            packet_json    TEXT,
            report_path    TEXT,
            updated_at     TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, snapshot_date)
        )
    """,
    "data_freshness": """
        CREATE TABLE IF NOT EXISTS data_freshness (
            ticker        TEXT NOT NULL,
            source_name   TEXT NOT NULL,
            last_updated  TIMESTAMP,
            record_count  INTEGER,
            status        TEXT,
            PRIMARY KEY (ticker, source_name)
        )
    """,
}


# ---------------------------------------------------------------------------
# Connection & schema
# ---------------------------------------------------------------------------

def get_connection(db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection, creating the database and tables if needed.

    Args:
        db_path: Path to the .duckdb file. Defaults to
                 .notlocal/data/personal-investor/db/research.duckdb relative
                 to the project root.

    Returns:
        A ``duckdb.DuckDBPyConnection`` ready for queries.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = duckdb.connect(path)
    ensure_schema(conn)
    return conn


def ensure_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create all research tables if they do not already exist.

    Safe to call multiple times — every statement uses IF NOT EXISTS.
    """
    for ddl in _TABLES.values():
        conn.execute(ddl)


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------

def _upsert(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    records: list[dict],
    key_cols: list[str],
) -> int:
    """Generic INSERT OR REPLACE for a list of dicts.

    DuckDB supports INSERT OR REPLACE when a primary key is defined.
    We build a parameterised INSERT statement from the first record's keys.

    Returns:
        Number of records upserted.
    """
    if not records:
        return 0

    # Normalise: every record must have the same columns.
    columns = list(records[0].keys())

    # Ensure updated_at is populated.
    now = datetime.utcnow()
    for rec in records:
        rec.setdefault("updated_at", now)

    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)

    # DuckDB supports INSERT OR REPLACE for tables with primary keys.
    sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"

    rows = [tuple(rec.get(c) for c in columns) for rec in records]
    conn.executemany(sql, rows)
    return len(rows)


def upsert_fundamentals(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``company_fundamentals``.

    Each dict must include at least ``ticker`` and ``period`` (the primary key).

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "company_fundamentals", records, ["ticker", "period"])


def upsert_earnings(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``earnings``.

    Each dict must include at least ``ticker`` and ``fiscal_period``.

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "earnings", records, ["ticker", "fiscal_period"])


def upsert_prices(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``prices``.

    Each dict must include at least ``ticker`` and ``date``.

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "prices", records, ["ticker", "date"])


def upsert_valuation(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``valuation``.

    Each dict must include at least ``ticker`` and ``date``.

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "valuation", records, ["ticker", "date"])


def upsert_sentiment(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert rows into ``sentiment_observations``.

    Sentiment observations have no natural primary key, so this appends.
    Callers should deduplicate by ``source_id`` before calling if needed.

    Returns:
        Number of records inserted.
    """
    if not records:
        return 0

    now = datetime.utcnow()
    columns = list(records[0].keys())
    for rec in records:
        rec.setdefault("updated_at", now)

    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)
    sql = f"INSERT INTO sentiment_observations ({col_list}) VALUES ({placeholders})"

    rows = [tuple(rec.get(c) for c in columns) for rec in records]
    conn.executemany(sql, rows)
    return len(rows)


def upsert_claims(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``investor_claims``.

    Each dict must include at least ``claim_id``.

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "investor_claims", records, ["claim_id"])


def upsert_research_snapshot(conn: duckdb.DuckDBPyConnection, records: list[dict]) -> int:
    """Insert or replace rows in ``research_snapshots``.

    Each dict must include at least ``ticker`` and ``snapshot_date``.

    Returns:
        Number of records upserted.
    """
    return _upsert(conn, "research_snapshots", records, ["ticker", "snapshot_date"])


# ---------------------------------------------------------------------------
# Freshness tracking
# ---------------------------------------------------------------------------

def get_freshness(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    source_name: str,
) -> Optional[datetime]:
    """Return the last-updated timestamp for a ticker/source pair, or None.

    Args:
        conn: Active DuckDB connection.
        ticker: Stock ticker symbol (e.g. ``"AAPL"``).
        source_name: Data source identifier (e.g. ``"yahoo_prices"``).

    Returns:
        A ``datetime`` of the last successful update, or ``None`` if no
        record exists.
    """
    result = conn.execute(
        "SELECT last_updated FROM data_freshness WHERE ticker = ? AND source_name = ?",
        [ticker, source_name],
    ).fetchone()
    if result and result[0]:
        ts = result[0]
        if isinstance(ts, datetime):
            return ts
        # DuckDB may return a string; parse it.
        return datetime.fromisoformat(str(ts))
    return None


def update_freshness(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    source_name: str,
    count: int,
    status: str = "ok",
) -> None:
    """Update the data_freshness tracker for a ticker/source pair.

    Args:
        conn: Active DuckDB connection.
        ticker: Stock ticker symbol.
        source_name: Data source identifier.
        count: Number of records ingested in this refresh.
        status: Short status string (default ``"ok"``).
    """
    now = datetime.utcnow()
    conn.execute(
        """
        INSERT OR REPLACE INTO data_freshness
            (ticker, source_name, last_updated, record_count, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        [ticker, source_name, now, count, status],
    )


# ---------------------------------------------------------------------------
# Query helpers (used by packet_builder and analytics)
# ---------------------------------------------------------------------------

def query_fundamentals(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    limit: Optional[int] = None,
) -> list[dict]:
    """Return fundamentals for *ticker* ordered by period descending.

    Args:
        limit: Maximum number of quarters to return. ``None`` returns all.
    """
    sql = (
        "SELECT * FROM company_fundamentals "
        "WHERE ticker = ? ORDER BY period DESC"
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    cols = [d[0] for d in conn.execute(sql, [ticker]).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, [ticker]).fetchall()]


def query_earnings(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    limit: Optional[int] = None,
) -> list[dict]:
    """Return earnings rows for *ticker* ordered by fiscal_period descending."""
    sql = (
        "SELECT * FROM earnings WHERE ticker = ? ORDER BY fiscal_period DESC"
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    cols = [d[0] for d in conn.execute(sql, [ticker]).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, [ticker]).fetchall()]


def query_prices(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """Return price rows for *ticker*, optionally filtered by date range."""
    conditions = ["ticker = ?"]
    params: list = [ticker]
    if start_date:
        conditions.append("date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("date <= ?")
        params.append(end_date)
    sql = f"SELECT * FROM prices WHERE {' AND '.join(conditions)} ORDER BY date DESC"
    cols = [d[0] for d in conn.execute(sql, params).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, params).fetchall()]


def query_valuation(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    limit: int = 1,
) -> list[dict]:
    """Return the most recent valuation row(s) for *ticker*."""
    sql = (
        "SELECT * FROM valuation WHERE ticker = ? ORDER BY date DESC "
        f"LIMIT {int(limit)}"
    )
    cols = [d[0] for d in conn.execute(sql, [ticker]).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, [ticker]).fetchall()]


def query_sentiment(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    days_back: int = 180,
) -> list[dict]:
    """Return sentiment observations for *ticker* within *days_back* days."""
    sql = (
        "SELECT * FROM sentiment_observations "
        f"WHERE ticker = ? AND date >= current_date - INTERVAL '{days_back}' DAY "
        "ORDER BY date DESC"
    )
    result = conn.execute(sql, [ticker])
    cols = [d[0] for d in result.description]
    return [dict(zip(cols, row)) for row in result.fetchall()]


def query_claims(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
    status: Optional[str] = None,
) -> list[dict]:
    """Return investor claims for *ticker*, optionally filtered by status."""
    conditions = ["ticker = ?"]
    params: list = [ticker]
    if status:
        conditions.append("verification_status = ?")
        params.append(status)
    sql = (
        f"SELECT * FROM investor_claims WHERE {' AND '.join(conditions)} "
        "ORDER BY date DESC"
    )
    cols = [d[0] for d in conn.execute(sql, params).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, params).fetchall()]


def query_freshness_all(
    conn: duckdb.DuckDBPyConnection,
    ticker: str,
) -> list[dict]:
    """Return all data_freshness rows for *ticker*."""
    sql = "SELECT * FROM data_freshness WHERE ticker = ? ORDER BY source_name"
    cols = [d[0] for d in conn.execute(sql, [ticker]).description]
    return [dict(zip(cols, row)) for row in conn.execute(sql, [ticker]).fetchall()]
