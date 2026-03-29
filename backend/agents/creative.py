"""Creative Agent — generates content variants and creative briefs."""

import logging
from storage import get_db, log_agent

logger = logging.getLogger(__name__)


class CreativeAgent:
    name = "creative"
    description = "Generates content variants based on TRIBE insights and benchmarks"

    def __init__(self):
        self.status = "idle"
        self.variants_generated = 0

    def generate_brief(self, content_type: str, target_score: int = 80) -> dict:
        """Generate a creative brief based on learned patterns.

        Args:
            content_type: Format of the content (e.g. "video", "audio", "text").
            target_score: Desired TRIBE brain-engagement score (0-100).

        Returns:
            A dict with guidelines, structure, and target parameters.
        """
        db = get_db()
        patterns = db.execute(
            "SELECT pattern FROM patterns WHERE confidence > 0.6 "
            "ORDER BY confidence DESC LIMIT 10"
        ).fetchall()
        db.close()

        brief = {
            "content_type": content_type,
            "target_score": target_score,
            "guidelines": [row["pattern"] for row in patterns],
            "structure": {
                "hook": "Face + direct address in first 2 seconds",
                "body": "Scene change every 4 seconds, maintain audio engagement",
                "cta": "Place CTA when prefrontal activation peaks",
            },
        }

        self.variants_generated += 1
        return brief

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "variants_generated": self.variants_generated,
        }
