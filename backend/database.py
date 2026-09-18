import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support_ai.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    from_email TEXT,
    topic TEXT,
    sentiment TEXT,
    sentiment_score REAL,
    urgency TEXT,
    phishing_detected INTEGER,
    risk_level TEXT,
    result_json TEXT NOT NULL
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def save_analysis(result):
    customer = result.get("customer_intelligence", {})
    security = result.get("security_intelligence", {})
    risk = result.get("risk", {})
    sender = result.get("sender") or {}
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO messages
            (created_at, raw_text, from_email, topic, sentiment, sentiment_score,
             urgency, phishing_detected, risk_level, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                result.get("raw", "")[:20000],
                sender.get("email"),
                customer.get("topic", "General"),
                customer.get("sentiment", "Neutral"),
                customer.get("sentiment_score", 0.0),
                customer.get("urgency", "Normal"),
                1 if security.get("phishing_detected") else 0,
                risk.get("level", "LOW"),
                json.dumps(result, ensure_ascii=False),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_messages(limit=50, offset=0):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, created_at, raw_text, from_email, topic, sentiment,
                   sentiment_score, urgency, phishing_detected, risk_level
            FROM messages
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_results(limit=50, offset=0):
    rows = list_messages(limit=limit, offset=offset)
    results = []
    for row in rows:
        result = {
            "id": row["id"],
            "created_at": row["created_at"],
            "from_email": row["from_email"],
            "raw_text": row["raw_text"],
            "topic": row["topic"],
            "sentiment": row["sentiment"],
            "sentiment_score": row["sentiment_score"],
            "urgency": row["urgency"],
            "phishing_detected": bool(row["phishing_detected"]),
            "risk_level": row["risk_level"],
        }
        results.append(result)
    return results


def recent_ids(limit=100):
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id FROM messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [r["id"] for r in rows]
    finally:
        conn.close()