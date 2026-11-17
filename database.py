"""
CreatorFlow Database Module.
Handles SQLite connection, schema migrations, and parameterized CRUD operations.
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import DATABASE_FILE


def get_db_connection() -> sqlite3.Connection:
    """Establish and return a SQLite database connection with row factory configured."""
    conn = sqlite3.connect(DATABASE_FILE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrent read/write stability
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    """
    Initialize SQLite database tables and indexes automatically.
    Safe to call multiple times (idempotent).
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS content_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id TEXT UNIQUE NOT NULL,
        original_input TEXT NOT NULL,
        generated_output TEXT NOT NULL,
        content_type TEXT NOT NULL,
        language TEXT NOT NULL DEFAULT 'English',
        evaluation_score REAL,
        metadata_json TEXT DEFAULT '{}',
        is_saved INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    index_sqls = [
        "CREATE INDEX IF NOT EXISTS idx_content_items_type ON content_items(content_type);",
        "CREATE INDEX IF NOT EXISTS idx_content_items_created ON content_items(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_content_items_saved ON content_items(is_saved);",
        "CREATE INDEX IF NOT EXISTS idx_content_items_lang ON content_items(language);",
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        for idx in index_sqls:
            cursor.execute(idx)
        conn.commit()


def save_content(
    original_input: str,
    generated_output: str,
    content_type: str,
    language: str = "English",
    evaluation_score: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    is_saved: int = 1,
    content_id: Optional[str] = None,
) -> str:
    """
    Save or update a generated content item.
    Returns the content_id string.
    """
    if not content_id:
        content_id = f"cf_{uuid.uuid4().hex[:12]}"

    metadata_str = json.dumps(metadata or {}, ensure_ascii=False)

    insert_sql = """
    INSERT INTO content_items (
        content_id, original_input, generated_output, content_type,
        language, evaluation_score, metadata_json, is_saved, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
    """

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            insert_sql,
            (
                content_id,
                original_input.strip(),
                generated_output.strip(),
                content_type.strip(),
                language.strip(),
                evaluation_score,
                metadata_str,
                is_saved,
            ),
        )
        conn.commit()

    return content_id


def get_content_items(
    search_query: Optional[str] = None,
    content_type: Optional[str] = None,
    language: Optional[str] = None,
    is_saved_only: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Retrieve content items with filtering and search capabilities.
    Uses parameterized SQL queries.
    """
    conditions = []
    params: List[Any] = []

    if is_saved_only:
        conditions.append("is_saved = 1")

    if content_type and content_type != "All":
        conditions.append("content_type = ?")
        params.append(content_type)

    if language and language != "All":
        conditions.append("language = ?")
        params.append(language)

    if search_query and search_query.strip():
        wildcard = f"%{search_query.strip()}%"
        conditions.append(
            "(original_input LIKE ? OR generated_output LIKE ? OR metadata_json LIKE ?)"
        )
        params.extend([wildcard, wildcard, wildcard])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    SELECT id, content_id, original_input, generated_output, content_type,
           language, evaluation_score, metadata_json, is_saved, created_at
    FROM content_items
    {where_clause}
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item.get("metadata_json") or "{}")
        except Exception:
            item["metadata"] = {}
        results.append(item)

    return results


def get_content_by_id(content_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single content record by content_id."""
    query = """
    SELECT id, content_id, original_input, generated_output, content_type,
           language, evaluation_score, metadata_json, is_saved, created_at
    FROM content_items
    WHERE content_id = ?
    LIMIT 1
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (content_id,))
        row = cursor.fetchone()

    if not row:
        return None

    item = dict(row)
    try:
        item["metadata"] = json.loads(item.get("metadata_json") or "{}")
    except Exception:
        item["metadata"] = {}
    return item


def delete_content(content_id: str) -> bool:
    """Delete a content item by content_id."""
    query = "DELETE FROM content_items WHERE content_id = ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (content_id,))
        conn.commit()
        return cursor.rowcount > 0


def update_content_score(
    content_id: str, score: float, metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Update evaluation score and metadata for an existing content item."""
    if metadata is not None:
        metadata_str = json.dumps(metadata, ensure_ascii=False)
        query = """
        UPDATE content_items
        SET evaluation_score = ?, metadata_json = ?
        WHERE content_id = ?
        """
        params = (score, metadata_str, content_id)
    else:
        query = """
        UPDATE content_items
        SET evaluation_score = ?
        WHERE content_id = ?
        """
        params = (score, content_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Calculate and return aggregate analytics from SQLite for the dashboard.
    All statistics are derived directly from the database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total generated count
        cursor.execute("SELECT COUNT(*) FROM content_items")
        total_items = cursor.fetchone()[0]

        # Total saved count
        cursor.execute("SELECT COUNT(*) FROM content_items WHERE is_saved = 1")
        total_saved = cursor.fetchone()[0]

        # Average evaluation score for evaluated items
        cursor.execute(
            "SELECT AVG(evaluation_score) FROM content_items WHERE evaluation_score IS NOT NULL"
        )
        avg_score_raw = cursor.fetchone()[0]
        avg_score = round(float(avg_score_raw), 1) if avg_score_raw is not None else 0.0

        # Distribution by content_type
        cursor.execute(
            """
            SELECT content_type, COUNT(*) as count
            FROM content_items
            GROUP BY content_type
            ORDER BY count DESC
            """
        )
        type_rows = cursor.fetchall()
        type_distribution = [
            {"content_type": row["content_type"], "count": row["count"]}
            for row in type_rows
        ]

        # Distribution by language
        cursor.execute(
            """
            SELECT language, COUNT(*) as count
            FROM content_items
            GROUP BY language
            ORDER BY count DESC
            """
        )
        lang_rows = cursor.fetchall()
        lang_distribution = [
            {"language": row["language"], "count": row["count"]} for row in lang_rows
        ]

        # Recent 6 items
        cursor.execute(
            """
            SELECT id, content_id, original_input, generated_output, content_type,
                   language, evaluation_score, metadata_json, created_at
            FROM content_items
            ORDER BY created_at DESC
            LIMIT 6
            """
        )
        recent_rows = cursor.fetchall()
        recent_items = []
        for r in recent_rows:
            rec = dict(r)
            try:
                rec["metadata"] = json.loads(rec.get("metadata_json") or "{}")
            except Exception:
                rec["metadata"] = {}
            recent_items.append(rec)

    return {
        "total_generated": total_items,
        "total_saved": total_saved,
        "avg_evaluation_score": avg_score,
        "type_distribution": type_distribution,
        "lang_distribution": lang_distribution,
        "recent_items": recent_items,
    }

