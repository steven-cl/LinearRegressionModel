import os
import sqlite3
from typing import List, Tuple, Optional, Union, Sequence

# Absolute path to the SQLite database file (adjust if needed)
DB_PATH = os.path.join(os.path.dirname(__file__), "regressionModel.db")


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite3 connection to the regressionModel.db.
    """
    return sqlite3.connect(DB_PATH)


def _normalize_xy(value: Union[str, Sequence, int, float]) -> str:
    """
    Normalize x or y input to a comma-separated string representation.
    If it's already a string, returns as-is.
    If it's a sequence (list/tuple), joins items by comma.
    Otherwise casts to string directly.
    """
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return ",".join(str(v) for v in value)
    return str(value)


def search_models(name_fragment: str) -> List[Tuple[int, str]]:
    """
    Search models whose name partially matches name_fragment.
    Returns a list of (id, model_name).
    Uses case-insensitive LIKE and sorts by closest length difference first.
    """
    fragment = f"%{name_fragment.strip()}%"
    query = """
        SELECT id, model_name
        FROM regression_model
        WHERE LOWER(model_name) LIKE LOWER(?)
        ORDER BY ABS(LENGTH(model_name) - ?), model_name ASC
    """
    conn = get_connection()
    try:
        cur = conn.execute(query, (fragment, len(name_fragment.strip())))
        return cur.fetchall()
    finally:
        conn.close()


def get_model_xy_by_id(model_id: int) -> Optional[Tuple[str, str]]:
    """
    Given a model id, return (x, y) as stored strings.
    Returns None if not found.
    """
    query = """
        SELECT x, y
        FROM regression_model
        WHERE id = ?
        LIMIT 1
    """
    conn = get_connection()
    try:
        cur = conn.execute(query, (model_id,))
        row = cur.fetchone()
        return row if row else None
    finally:
        conn.close()


def insert_model(model_name: str, x, y) -> int:
    """
    Insert a new regression model row with model_name, x, y.
    Returns inserted row id.
    Raises RuntimeError if lastrowid is unexpectedly None.
    """
    x_str = _normalize_xy(x)
    y_str = _normalize_xy(y)
    query = """
        INSERT INTO regression_model (model_name, x, y)
        VALUES (?, ?, ?)
    """
    conn = get_connection()
    try:
        cur = conn.execute(query, (str(model_name), x_str, y_str))
        conn.commit()
        rowid = cur.lastrowid
        if rowid is None:
            raise RuntimeError("Failed to retrieve lastrowid after insert.")
        return rowid
    finally:
        conn.close()


def update_model_xy(model_id: int, x, y) -> bool:
    """
    Update x and y of an existing row by id.
    Returns True if a row was actually updated.
    """
    x_str = _normalize_xy(x)
    y_str = _normalize_xy(y)
    query = """
        UPDATE regression_model
        SET x = ?, y = ?
        WHERE id = ?
    """
    conn = get_connection()
    try:
        cur = conn.execute(query, (x_str, y_str, model_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


__all__ = [
    "get_connection",
    "search_models",
    "get_model_xy_by_id",
    "insert_model",
    "update_model_xy",
]