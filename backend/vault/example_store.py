"""
Example Store — persists every scored content piece with full TRIBE brain data.
Auto-classifies as GOOD (score >= 75), BAD (score <= 45), NEUTRAL (46-74).

Source separation is strict and mandatory:
  "own"        — content you created and scored (calibration data)
  "competitor" — competitor content scanned for benchmarks
  "universal"  — any source, used only for brain-level rules

The learner agent reads calibrated own data to update brain weights.
Competitor data feeds only universal pattern analysis.
"""

import json
import time
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from config import settings

logger = logging.getLogger(__name__)

VAULT_DB_PATH = settings.db_path.parent / "vault.db"

VALID_SOURCES = {"own", "competitor", "universal"}


@dataclass
class ScoredExample:
    id: str
    filename: str
    modality: str  # video, audio, text
    classification: str  # GOOD, BAD, NEUTRAL
    overall_score: int
    hook_score: float

    # Region scores
    visual_avg: float
    auditory_avg: float
    language_avg: float
    decision_avg: float
    emotion_avg: float

    # Modality contribution
    visual_pct: float
    audio_pct: float
    text_pct: float

    # Moments
    weak_moment_count: int
    peak_moment_count: int

    # Full result blob (JSON)
    full_result: str

    # Source — MUST be set explicitly. No silent defaults in production paths.
    source: str = "own"  # "own" | "competitor" | "universal"

    # Metadata
    platform: str = ""
    audience_segment: str = ""
    tags: str = ""  # comma-separated
    notes: str = ""
    created_at: float = 0

    # Real-world performance (added later; only meaningful for own data)
    real_ctr: Optional[float] = None
    real_conversion: Optional[float] = None
    real_watch_time: Optional[float] = None


def _get_vault_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(VAULT_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS examples (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            modality TEXT NOT NULL,
            classification TEXT NOT NULL,
            overall_score INTEGER,
            hook_score REAL,
            visual_avg REAL,
            auditory_avg REAL,
            language_avg REAL,
            decision_avg REAL,
            emotion_avg REAL,
            visual_pct REAL,
            audio_pct REAL,
            text_pct REAL,
            weak_moment_count INTEGER DEFAULT 0,
            peak_moment_count INTEGER DEFAULT 0,
            full_result TEXT,
            source TEXT NOT NULL DEFAULT 'own',
            platform TEXT DEFAULT '',
            audience_segment TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at REAL DEFAULT (unixepoch()),
            real_ctr REAL,
            real_conversion REAL,
            real_watch_time REAL
        );
        CREATE INDEX IF NOT EXISTS idx_examples_class ON examples(classification);
        CREATE INDEX IF NOT EXISTS idx_examples_score ON examples(overall_score);
        CREATE INDEX IF NOT EXISTS idx_examples_platform ON examples(platform);
        CREATE INDEX IF NOT EXISTS idx_examples_source ON examples(source);
    """)
    conn.commit()
    _migrate_add_source_column(conn)
    return conn


def _migrate_add_source_column(conn: sqlite3.Connection) -> None:
    """Add source column to existing databases that pre-date this change."""
    existing = {
        row[1]
        for row in conn.execute("PRAGMA table_info(examples)").fetchall()
    }
    if "source" not in existing:
        conn.execute(
            "ALTER TABLE examples ADD COLUMN source TEXT NOT NULL DEFAULT 'own'"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_examples_source ON examples(source)"
        )
        conn.commit()
        logger.info("Migrated examples table: added source column (default='own')")


class ExampleStore:
    """Stores and retrieves scored content examples with strict source separation."""

    def __init__(self):
        self._db = _get_vault_db()

    def classify(self, score: int) -> str:
        if score >= 75:
            return "GOOD"
        elif score <= 45:
            return "BAD"
        return "NEUTRAL"

    def add(
        self,
        score_result: dict,
        filename: str = "",
        modality: str = "",
        platform: str = "",
        audience_segment: str = "",
        tags: str = "",
        notes: str = "",
        source: str = "own",
    ) -> ScoredExample:
        """Add a scored content piece to the vault.

        Args:
            source: Data origin — "own", "competitor", or "universal".
                    Caller must pass this explicitly. The default "own" exists
                    only for backward compatibility; new call sites should always
                    supply it.
        """
        import hashlib

        if source not in VALID_SOURCES:
            raise ValueError(
                f"Invalid source '{source}'. Must be one of: {VALID_SOURCES}"
            )

        example_id = hashlib.md5(f"{filename}:{time.time()}".encode()).hexdigest()[:12]
        overall = score_result.get("overall_score", 0)
        classification = self.classify(overall)

        example = ScoredExample(
            id=example_id,
            filename=filename,
            modality=modality,
            classification=classification,
            overall_score=overall,
            hook_score=score_result.get("hook_score", 0),
            visual_avg=score_result.get("visual_avg", 0),
            auditory_avg=score_result.get("auditory_avg", 0),
            language_avg=score_result.get("language_avg", 0),
            decision_avg=score_result.get("decision_avg", 0),
            emotion_avg=score_result.get("emotion_avg", 0),
            visual_pct=score_result.get("visual_pct", 33),
            audio_pct=score_result.get("audio_pct", 33),
            text_pct=score_result.get("text_pct", 34),
            weak_moment_count=len(score_result.get("weak_moments", [])),
            peak_moment_count=len(score_result.get("peak_moments", [])),
            full_result=json.dumps(score_result),
            source=source,
            platform=platform,
            audience_segment=audience_segment,
            tags=tags,
            notes=notes,
            created_at=time.time(),
        )

        self._db.execute(
            """INSERT OR REPLACE INTO examples
            (id, filename, modality, classification, overall_score, hook_score,
             visual_avg, auditory_avg, language_avg, decision_avg, emotion_avg,
             visual_pct, audio_pct, text_pct, weak_moment_count, peak_moment_count,
             full_result, source, platform, audience_segment, tags, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                example.id,
                example.filename,
                example.modality,
                example.classification,
                example.overall_score,
                example.hook_score,
                example.visual_avg,
                example.auditory_avg,
                example.language_avg,
                example.decision_avg,
                example.emotion_avg,
                example.visual_pct,
                example.audio_pct,
                example.text_pct,
                example.weak_moment_count,
                example.peak_moment_count,
                example.full_result,
                example.source,
                example.platform,
                example.audience_segment,
                example.tags,
                example.notes,
                example.created_at,
            ),
        )
        self._db.commit()

        logger.info(
            f"Example stored: {filename} → {classification} "
            f"(score: {overall}, source: {source})"
        )
        return example

    def update_real_metrics(
        self,
        example_id: str,
        ctr: float = None,
        conversion: float = None,
        watch_time: float = None,
    ):
        """Add real-world performance data to an example.

        Only meaningful for own-source examples, but not enforced here — the
        vault layer guards this via record_score().
        """
        updates = []
        params = []
        if ctr is not None:
            updates.append("real_ctr = ?")
            params.append(ctr)
        if conversion is not None:
            updates.append("real_conversion = ?")
            params.append(conversion)
        if watch_time is not None:
            updates.append("real_watch_time = ?")
            params.append(watch_time)

        if updates:
            params.append(example_id)
            self._db.execute(
                f"UPDATE examples SET {', '.join(updates)} WHERE id = ?", params
            )
            self._db.commit()

    # ── Retrieval ──────────────────────────────────────────

    def get_all(
        self,
        classification: str = None,
        source: str = None,
        limit: int = 500,
    ) -> List[dict]:
        """Fetch examples, optionally filtered by classification and/or source."""
        clauses = []
        params: list = []

        if classification:
            clauses.append("classification = ?")
            params.append(classification)
        if source:
            if source not in VALID_SOURCES:
                raise ValueError(f"Invalid source filter '{source}'")
            clauses.append("source = ?")
            params.append(source)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        rows = self._db.execute(
            f"SELECT * FROM examples {where} ORDER BY created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [dict(r) for r in rows]

    def get_good(self, limit: int = 200) -> List[dict]:
        """All GOOD examples regardless of source (for universal analysis)."""
        return self.get_all("GOOD", limit=limit)

    def get_bad(self, limit: int = 200) -> List[dict]:
        """All BAD examples regardless of source (for universal analysis)."""
        return self.get_all("BAD", limit=limit)

    def get_own(self, classification: str = None, limit: int = 200) -> List[dict]:
        """Return only source='own' examples.

        Used by the Learner agent when updating brain weights.
        Never mixes with competitor data.
        """
        return self.get_all(classification=classification, source="own", limit=limit)

    def get_competitor(self, classification: str = None, limit: int = 200) -> List[dict]:
        """Return only source='competitor' examples.

        Used for benchmark analysis. Never fed into weight updates.
        """
        return self.get_all(
            classification=classification, source="competitor", limit=limit
        )

    def get_calibrated(self, limit: int = 200) -> List[dict]:
        """Return own examples that have at least one real performance metric.

        These are the gold-standard calibration set: own content with known
        real-world outcomes. Calibrated patterns derived from this set drive
        deploy decisions and weight updates.
        """
        rows = self._db.execute(
            """SELECT * FROM examples
               WHERE source = 'own'
                 AND (real_ctr IS NOT NULL
                      OR real_conversion IS NOT NULL
                      OR real_watch_time IS NOT NULL)
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Stats ──────────────────────────────────────────────

    def get_stats(self) -> dict:
        total = self._db.execute("SELECT COUNT(*) FROM examples").fetchone()[0]
        good = self._db.execute(
            "SELECT COUNT(*) FROM examples WHERE classification = 'GOOD'"
        ).fetchone()[0]
        bad = self._db.execute(
            "SELECT COUNT(*) FROM examples WHERE classification = 'BAD'"
        ).fetchone()[0]
        neutral = self._db.execute(
            "SELECT COUNT(*) FROM examples WHERE classification = 'NEUTRAL'"
        ).fetchone()[0]
        with_metrics = self._db.execute(
            "SELECT COUNT(*) FROM examples "
            "WHERE real_ctr IS NOT NULL OR real_conversion IS NOT NULL"
        ).fetchone()[0]

        avg_good = (
            self._db.execute(
                "SELECT AVG(overall_score) FROM examples WHERE classification = 'GOOD'"
            ).fetchone()[0]
            or 0
        )
        avg_bad = (
            self._db.execute(
                "SELECT AVG(overall_score) FROM examples WHERE classification = 'BAD'"
            ).fetchone()[0]
            or 0
        )

        # Per-source counts
        source_rows = self._db.execute(
            "SELECT source, COUNT(*) FROM examples GROUP BY source"
        ).fetchall()
        by_source = {row[0]: row[1] for row in source_rows}

        # Calibrated = own + has metrics
        calibrated_count = self._db.execute(
            """SELECT COUNT(*) FROM examples
               WHERE source = 'own'
                 AND (real_ctr IS NOT NULL
                      OR real_conversion IS NOT NULL
                      OR real_watch_time IS NOT NULL)"""
        ).fetchone()[0]

        return {
            "total": total,
            "good": good,
            "bad": bad,
            "neutral": neutral,
            "with_real_metrics": with_metrics,
            "avg_good_score": round(avg_good, 1),
            "avg_bad_score": round(avg_bad, 1),
            "by_source": {
                "own": by_source.get("own", 0),
                "competitor": by_source.get("competitor", 0),
                "universal": by_source.get("universal", 0),
            },
            "calibrated": calibrated_count,
            "platforms": [
                r[0]
                for r in self._db.execute(
                    "SELECT DISTINCT platform FROM examples WHERE platform != ''"
                ).fetchall()
            ],
        }
