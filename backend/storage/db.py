"""SQLite storage for TRIBE marketing intelligence."""

import sqlite3
import json
import time
from pathlib import Path
from config import settings


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS scores (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            filename         TEXT    NOT NULL,
            modality         TEXT    NOT NULL,
            overall_score    INTEGER,
            duration_seconds INTEGER,
            visual_avg       REAL,
            auditory_avg     REAL,
            language_avg     REAL,
            decision_avg     REAL,
            emotion_avg      REAL,
            visual_pct       REAL,
            audio_pct        REAL,
            text_pct         REAL,
            hook_score       REAL,
            full_result      TEXT,   -- JSON blob
            created_at       REAL    DEFAULT (unixepoch())
        );

        CREATE TABLE IF NOT EXISTS benchmarks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,  -- industry, format, audience
            metric      TEXT    NOT NULL,
            value       REAL    NOT NULL,
            sample_size INTEGER DEFAULT 1,
            updated_at  REAL    DEFAULT (unixepoch())
        );

        CREATE TABLE IF NOT EXISTS patterns (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern        TEXT    NOT NULL,
            confidence     REAL    DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 1,
            discovered_at  REAL    DEFAULT (unixepoch()),
            last_confirmed REAL    DEFAULT (unixepoch())
        );

        CREATE TABLE IF NOT EXISTS competitors (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            url           TEXT,
            last_scanned  REAL,
            content_count INTEGER DEFAULT 0,
            avg_score     REAL    DEFAULT 0,
            status        TEXT    DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS agent_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            agent      TEXT    NOT NULL,
            action     TEXT    NOT NULL,
            detail     TEXT,
            created_at REAL    DEFAULT (unixepoch())
        );
    """)
    conn.commit()


def save_score(conn: sqlite3.Connection, filename: str, modality: str, score_dict: dict) -> None:
    conn.execute(
        """INSERT INTO scores
               (filename, modality, overall_score, duration_seconds,
                visual_avg, auditory_avg, language_avg, decision_avg, emotion_avg,
                visual_pct, audio_pct, text_pct, hook_score, full_result)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            filename,
            modality,
            score_dict["overall_score"],
            score_dict["duration_seconds"],
            score_dict["visual_avg"],
            score_dict["auditory_avg"],
            score_dict["language_avg"],
            score_dict["decision_avg"],
            score_dict["emotion_avg"],
            score_dict["visual_pct"],
            score_dict["audio_pct"],
            score_dict["text_pct"],
            score_dict["hook_score"],
            json.dumps(score_dict),
        ),
    )
    conn.commit()


def get_scores(conn: sqlite3.Connection, limit: int = 50) -> list:
    rows = conn.execute(
        "SELECT * FROM scores ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_benchmarks(conn: sqlite3.Connection, category: str = None) -> list:
    if category:
        rows = conn.execute(
            "SELECT * FROM benchmarks WHERE category = ?", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM benchmarks").fetchall()
    return [dict(r) for r in rows]


def save_pattern(conn: sqlite3.Connection, pattern: str, confidence: float = 0.5) -> None:
    conn.execute(
        "INSERT INTO patterns (pattern, confidence) VALUES (?, ?)",
        (pattern, confidence),
    )
    conn.commit()


def get_patterns(conn: sqlite3.Connection, limit: int = 50) -> list:
    rows = conn.execute(
        "SELECT * FROM patterns ORDER BY confidence DESC, discovered_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def log_agent(conn: sqlite3.Connection, agent: str, action: str, detail: str = None) -> None:
    conn.execute(
        "INSERT INTO agent_logs (agent, action, detail) VALUES (?, ?, ?)",
        (agent, action, detail),
    )
    conn.commit()


def get_agent_logs(conn: sqlite3.Connection, agent: str = None, limit: int = 100) -> list:
    if agent:
        rows = conn.execute(
            "SELECT * FROM agent_logs WHERE agent = ? ORDER BY created_at DESC LIMIT ?",
            (agent, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
