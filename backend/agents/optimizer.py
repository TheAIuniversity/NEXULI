"""Optimizer Agent — takes TRIBE scores and recommends fixes."""

import logging
from storage import get_db, log_agent

logger = logging.getLogger(__name__)


class OptimizerAgent:
    name = "optimizer"
    description = "Analyzes TRIBE scores and generates optimization recommendations"

    def __init__(self):
        self.status = "idle"
        self.recommendations_count = 0

    def optimize(self, score_result: dict) -> list:
        """Generate optimization recommendations from a ContentScore dict.

        Args:
            score_result: Output of ContentScore.to_dict().

        Returns:
            List of recommendation dicts with priority, area, issue, and fix.
        """
        recommendations = []

        # Hook quality
        if score_result.get("hook_score", 0) < 60:
            recommendations.append({
                "priority": "high",
                "area": "hook",
                "issue": "Weak opening — hook score below 60",
                "fix": "Add a face, question, or surprising visual in the first 2 seconds.",
            })

        # Weak moment patches
        for wm in score_result.get("weak_moments", []):
            recommendations.append({
                "priority": "high" if wm["severity"] == "critical" else "medium",
                "area": f"{wm['start']:.0f}s-{wm['end']:.0f}s",
                "issue": wm["reason"],
                "fix": wm["recommendation"],
            })

        # Modality balance
        v_pct = score_result.get("visual_pct", 33)
        a_pct = score_result.get("audio_pct", 33)
        if v_pct < 20:
            recommendations.append({
                "priority": "medium",
                "area": "visual",
                "issue": f"Visual only carrying {v_pct:.0f}% — underutilized",
                "fix": "Add more visual variety, B-roll, or text overlays to support the audio.",
            })
        if a_pct < 20:
            recommendations.append({
                "priority": "medium",
                "area": "audio",
                "issue": f"Audio only carrying {a_pct:.0f}% — underutilized",
                "fix": "Add voiceover, music, or sound effects to complement visuals.",
            })

        # Overall floor check
        if score_result.get("overall_score", 0) < 50:
            recommendations.append({
                "priority": "critical",
                "area": "overall",
                "issue": "Overall score below 50 — content unlikely to perform",
                "fix": "Consider restructuring. Lead with strongest moment, cut weak sections.",
            })

        self.recommendations_count += len(recommendations)

        db = get_db()
        log_agent(
            db,
            self.name,
            "recommendations-generated",
            f"{len(recommendations)} fixes for score {score_result.get('overall_score', '?')}",
        )
        db.close()

        return recommendations

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "recommendations_count": self.recommendations_count,
        }
