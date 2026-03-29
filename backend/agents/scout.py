"""Scout Agent — monitors competitors and industry benchmarks."""

import logging
from storage import get_db, log_agent

logger = logging.getLogger(__name__)


class ScoutAgent:
    name = "scout"
    description = "Monitors competitor content and maintains industry benchmarks"

    def __init__(self):
        self.status = "idle"
        self.competitors_tracked = 0

    def add_competitor(self, name: str, url: str = None) -> None:
        """Add a competitor to the watchlist."""
        db = get_db()
        db.execute(
            "INSERT INTO competitors (name, url) VALUES (?, ?)",
            (name, url),
        )
        db.commit()
        log_agent(db, self.name, "competitor-added", name)
        db.close()
        self.competitors_tracked += 1

    def get_competitors(self) -> list:
        """Return all active competitors."""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM competitors WHERE status = 'active'"
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "competitors_tracked": self.competitors_tracked,
        }
