"""
Content Brain Map — pre-computed TRIBE brain profiles for every page/content piece.

Score all your content through TRIBE once. Store the brain map per URL/file.
When a lead visits a page, look up that page's brain profile instantly.
"""

import json
import time
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from config import settings

logger = logging.getLogger(__name__)

CONTENT_MAP_DB = settings.db_path.parent / "content_map.db"


@dataclass
class PageBrainProfile:
    """TRIBE brain profile for a single page/content piece."""
    url: str  # /pricing, /docs/getting-started, or video filename
    content_type: str  # "page", "video", "audio", "text", "blog"

    # Brain region scores (0-100) from TRIBE
    visual: float = 0
    auditory: float = 0
    language: float = 0
    decision: float = 0  # prefrontal
    emotion: float = 0   # default mode
    face: float = 0      # fusiform
    action: float = 0    # motor cortex
    social: float = 0    # social cognition
    attention: float = 0 # salience
    memory: float = 0    # encoding
    conflict: float = 0  # motivation/drive
    reward: float = 0    # reward processing

    # Dominant brain type for this content
    dominant_region: str = ""
    dominant_score: float = 0

    # Modality
    visual_pct: float = 33
    audio_pct: float = 33
    text_pct: float = 34

    # Overall TRIBE score
    tribe_score: float = 0
    hook_score: float = 0

    # Funnel stage this content serves
    funnel_stage: str = ""  # "awareness", "consideration", "decision"

    scored_at: float = 0

    def to_dict(self):
        return asdict(self)

    def get_region_scores(self) -> Dict[str, float]:
        return {
            "visual": self.visual,
            "auditory": self.auditory,
            "language": self.language,
            "decision": self.decision,
            "emotion": self.emotion,
            "face": self.face,
            "action": self.action,
            "social": self.social,
            "attention": self.attention,
            "memory": self.memory,
            "conflict": self.conflict,
            "reward": self.reward,
        }


def _get_content_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(CONTENT_MAP_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS content_profiles (
            url TEXT PRIMARY KEY,
            content_type TEXT NOT NULL,
            visual REAL DEFAULT 0, auditory REAL DEFAULT 0,
            language REAL DEFAULT 0, decision REAL DEFAULT 0,
            emotion REAL DEFAULT 0, face REAL DEFAULT 0,
            action REAL DEFAULT 0, social REAL DEFAULT 0,
            attention REAL DEFAULT 0, memory REAL DEFAULT 0,
            conflict REAL DEFAULT 0, reward REAL DEFAULT 0,
            dominant_region TEXT DEFAULT '',
            dominant_score REAL DEFAULT 0,
            visual_pct REAL DEFAULT 33, audio_pct REAL DEFAULT 33, text_pct REAL DEFAULT 34,
            tribe_score REAL DEFAULT 0, hook_score REAL DEFAULT 0,
            funnel_stage TEXT DEFAULT '',
            scored_at REAL DEFAULT 0
        );
    """)
    conn.commit()
    return conn


class ContentBrainMap:
    """Manages the pre-computed brain map of all content."""

    def __init__(self):
        self._db = _get_content_db()

    def add_profile(self, profile: PageBrainProfile):
        """Store a content piece's brain profile."""
        # Auto-detect dominant region
        scores = profile.get_region_scores()
        if scores:
            profile.dominant_region = max(scores, key=scores.get)
            profile.dominant_score = scores[profile.dominant_region]

        # Auto-detect funnel stage from brain profile
        if profile.decision > 65 or profile.reward > 60:
            profile.funnel_stage = "decision"
        elif profile.emotion > 60 or profile.social > 55:
            profile.funnel_stage = "consideration"
        else:
            profile.funnel_stage = "awareness"

        profile.scored_at = time.time()

        self._db.execute(
            """INSERT OR REPLACE INTO content_profiles
            (url, content_type, visual, auditory, language, decision, emotion, face,
             action, social, attention, memory, conflict, reward,
             dominant_region, dominant_score, visual_pct, audio_pct, text_pct,
             tribe_score, hook_score, funnel_stage, scored_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (profile.url, profile.content_type,
             profile.visual, profile.auditory, profile.language, profile.decision,
             profile.emotion, profile.face, profile.action, profile.social,
             profile.attention, profile.memory, profile.conflict, profile.reward,
             profile.dominant_region, profile.dominant_score,
             profile.visual_pct, profile.audio_pct, profile.text_pct,
             profile.tribe_score, profile.hook_score, profile.funnel_stage, profile.scored_at)
        )
        self._db.commit()

    def get_profile(self, url: str) -> Optional[PageBrainProfile]:
        """Get brain profile for a URL."""
        row = self._db.execute(
            "SELECT * FROM content_profiles WHERE url = ?", (url,)
        ).fetchone()
        if row:
            return PageBrainProfile(**{k: row[k] for k in row.keys()})
        return None

    def get_all(self) -> List[PageBrainProfile]:
        """Get all content profiles."""
        rows = self._db.execute("SELECT * FROM content_profiles ORDER BY scored_at DESC").fetchall()
        return [PageBrainProfile(**{k: r[k] for k in r.keys()}) for r in rows]

    def get_by_funnel(self, stage: str) -> List[PageBrainProfile]:
        """Get content by funnel stage."""
        rows = self._db.execute(
            "SELECT * FROM content_profiles WHERE funnel_stage = ?", (stage,)
        ).fetchall()
        return [PageBrainProfile(**{k: r[k] for k in r.keys()}) for r in rows]

    def get_stats(self) -> dict:
        total = self._db.execute("SELECT COUNT(*) FROM content_profiles").fetchone()[0]
        by_type = self._db.execute(
            "SELECT content_type, COUNT(*) as c FROM content_profiles GROUP BY content_type"
        ).fetchall()
        by_funnel = self._db.execute(
            "SELECT funnel_stage, COUNT(*) as c FROM content_profiles GROUP BY funnel_stage"
        ).fetchall()
        by_dominant = self._db.execute(
            "SELECT dominant_region, COUNT(*) as c FROM content_profiles GROUP BY dominant_region ORDER BY c DESC LIMIT 5"
        ).fetchall()

        return {
            "total_pages_scored": total,
            "by_type": {r["content_type"]: r["c"] for r in by_type},
            "by_funnel": {r["funnel_stage"]: r["c"] for r in by_funnel},
            "top_dominant_regions": {r["dominant_region"]: r["c"] for r in by_dominant},
        }
