"""Read-only MySQL MCP server for local Ouranious development.

Security is layered: use a dedicated MySQL account with SELECT/SHOW VIEW only,
then apply conservative SQL checks and result limits here as defense in depth.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import pymysql
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pymysql.cursors import DictCursor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ouranious_mysql_mcp")

mcp = FastMCP(
    "ouranious_mysql",
    instructions=(
        "Read-only inspection tools for the local Ouranious Knowledge Base MySQL database. "
        "Use these tools to inspect schemas and data instead of asking the user to paste query results. "
        "Only use read queries. Never attempt writes, DDL, stored procedures, or privilege changes. "
        "Returned rows may contain sensitive development data; request only the columns and rows needed."
    ),
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_$]+$")
_FORBIDDEN_SQL_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|UPSERT|CREATE|ALTER|DROP|TRUNCATE|RENAME|GRANT|REVOKE|"
    r"CALL|DO|HANDLER|LOAD\s+DATA|OUTFILE|DUMPFILE|INTO\s+OUTFILE|INTO\s+DUMPFILE|"
    r"LOCK|UNLOCK|GET_LOCK|RELEASE_LOCK|SLEEP|BENCHMARK|LOAD_FILE)\b",
    re.IGNORECASE,
)


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} must be between {minimum} and {maximum}")
    return value


DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_PORT = _env_int("MYSQL_PORT", 3306, 1, 65535)
DB_NAME = os.getenv("MYSQL_DATABASE", "ouranious_knowledge_base")
DB_USER = os.getenv("MYSQL_USER", "ouranious_inspector")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
CONNECT_TIMEOUT = _env_int("MYSQL_CONNECT_TIMEOUT", 5, 1, 30)
DEFAULT_ROW_LIMIT = _env_int("MYSQL_DEFAULT_ROW_LIMIT", 100, 1, 500)
MAX_ROW_LIMIT = _env_int("MYSQL_MAX_ROW_LIMIT", 250, 1, 1000)
MAX_QUERY_LENGTH = _env_int("MYSQL_MAX_QUERY_LENGTH", 12000, 100, 50000)
QUERY_TIMEOUT_MS = _env_int("MYSQL_QUERY_TIMEOUT_MS", 5000, 100, 60000)


def _connect():
    if not DB_PASSWORD:
        raise RuntimeError("MYSQL_PASSWORD is empty. Set it in the local .env file.")
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        connect_timeout=CONNECT_TIMEOUT,
        read_timeout=max(10, QUERY_TIMEOUT_MS // 1000 + 5),
        write_timeout=5,
        autocommit=True,
    )


def _json_safe(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (set, tuple)):
        return list(value)
    return str(value)


def _validate_identifier(value: str, label: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {label}. Use only letters, numbers, underscore, and dollar sign.")
    return value


def _validate_read_query(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")
    query = query.strip()
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query exceeds the maximum length of {MAX_QUERY_LENGTH} characters.")
    # Keep the interface deliberately conservative: one SELECT statement only.
    if ";" in query:
        raise ValueError("Multiple statements and semicolons are not allowed.")
    if "--" in query or "/*" in query or "*/" in query or "#" in query:
        raise ValueError("SQL comments are not allowed.")
    if not re.match(r"^SELECT\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed. Use the dedicated schema tools for inspection.")
    if _FORBIDDEN_SQL_RE.search(query):
        raise ValueError("The query contains a prohibited keyword or function.")
    if re.search(r"\bFOR\s+(UPDATE|SHARE)\b|\bLOCK\s+IN\s+SHARE\s+MODE\b", query, re.IGNORECASE):
        raise ValueError("Locking reads are not allowed.")
    return query


def _run(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            # MySQL supports this optimizer hint to bound execution time for SELECT.
            cursor.execute("SET SESSION max_execution_time = %s", (QUERY_TIMEOUT_MS,))
            cursor.execute(sql, params)
            return list(cursor.fetchall())
    finally:
        connection.close()


@mcp.tool()
def list_tables() -> dict[str, Any]:
    """List tables and views in the configured Ouranious database."""
    rows = _run(
        "SELECT TABLE_NAME AS table_name, TABLE_TYPE AS table_type "
        "FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME",
        (DB_NAME,),
    )
    return {"database": DB_NAME, "count": len(rows), "tables": rows}


@mcp.tool()
def describe_table(table_name: str) -> dict[str, Any]:
    """Return columns, data types, nullability, defaults, keys, and indexes for one table."""
    table_name = _validate_identifier(table_name, "table name")
    columns = _run(
        "SELECT COLUMN_NAME AS column_name, COLUMN_TYPE AS column_type, IS_NULLABLE AS is_nullable, "
        "COLUMN_DEFAULT AS column_default, COLUMN_KEY AS column_key, EXTRA AS extra, "
        "ORDINAL_POSITION AS ordinal_position "
        "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION",
        (DB_NAME, table_name),
    )
    if not columns:
        return {"table": table_name, "columns": [], "indexes": [], "foreign_keys": [], "message": "Table not found or no visible columns."}
    indexes = _run(
        "SELECT INDEX_NAME AS index_name, NON_UNIQUE AS non_unique, SEQ_IN_INDEX AS sequence, "
        "COLUMN_NAME AS column_name, INDEX_TYPE AS index_type "
        "FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY INDEX_NAME, SEQ_IN_INDEX",
        (DB_NAME, table_name),
    )
    foreign_keys = _run(
        "SELECT k.CONSTRAINT_NAME AS constraint_name, k.COLUMN_NAME AS column_name, "
        "k.REFERENCED_TABLE_NAME AS referenced_table, k.REFERENCED_COLUMN_NAME AS referenced_column "
        "FROM information_schema.KEY_COLUMN_USAGE k WHERE k.TABLE_SCHEMA = %s "
        "AND k.TABLE_NAME = %s AND k.REFERENCED_TABLE_NAME IS NOT NULL "
        "ORDER BY k.CONSTRAINT_NAME, k.ORDINAL_POSITION",
        (DB_NAME, table_name),
    )
    return {"table": table_name, "columns": columns, "indexes": indexes, "foreign_keys": foreign_keys}


@mcp.tool()
def read_query(query: str, row_limit: int = DEFAULT_ROW_LIMIT) -> dict[str, Any]:
    """Execute one read-only SELECT query and return a bounded number of rows.

    Query must be a single SELECT statement without comments or a trailing semicolon.
    Use row_limit to keep output concise; maximum is configured by MYSQL_MAX_ROW_LIMIT.
    """
    query = _validate_read_query(query)
    if not 1 <= row_limit <= MAX_ROW_LIMIT:
        raise ValueError(f"row_limit must be between 1 and {MAX_ROW_LIMIT}.")
    # Wrap the query so the MCP server itself enforces the result cap. The inner query
    # must not contain a semicolon, and the database account must remain read-only.
    bounded_sql = f"SELECT * FROM ({query}) AS mcp_read_result LIMIT {int(row_limit) + 1}"
    rows = _run(bounded_sql)
    truncated = len(rows) > row_limit
    rows = rows[:row_limit]
    return {
        "database": DB_NAME,
        "row_count_returned": len(rows),
        "truncated": truncated,
        "row_limit": row_limit,
        "rows": json.loads(json.dumps(rows, default=_json_safe)),
    }


@mcp.tool()
def get_table_counts(table_names: list[str]) -> dict[str, Any]:
    """Return approximate row counts from MySQL metadata for up to 30 named tables.

    InnoDB table counts are estimates, not exact counts. Use read_query for a precise count when needed.
    """
    if not table_names:
        raise ValueError("Provide at least one table name.")
    if len(table_names) > 30:
        raise ValueError("Request at most 30 tables at a time.")
    clean_names = [_validate_identifier(name, "table name") for name in table_names]
    placeholders = ",".join(["%s"] * len(clean_names))
    rows = _run(
        f"SELECT TABLE_NAME AS table_name, TABLE_ROWS AS approximate_rows "
        f"FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME IN ({placeholders}) "
        "ORDER BY TABLE_NAME",
        (DB_NAME, *clean_names),
    )
    return {"database": DB_NAME, "counts_are_approximate": True, "tables": rows}


if __name__ == "__main__":
    # Do not print to stdout: stdio is used by MCP for protocol messages.
    mcp.run(transport="stdio")
