"""Learning Agent — discovers patterns and calibrates predictions."""

import logging

logger = logging.getLogger(__name__)


class LearnerAgent:
    name = "learner"
    description = (
        "Discovers patterns from scored content and calibrates TRIBE predictions "
        "against real performance data"
    )

    def __init__(self):
        self.status = "idle"
        self.patterns_found = 0

    def analyze_scores(self) -> list:
        """Delegate to PatternVault for real analysis.

        Returns:
            List containing summary strings for the top universal and calibrated patterns.
        """
        try:
            from vault import PatternVault
            pv = PatternVault()
            result = pv.run_analysis()
            self.patterns_found += result.get("total_patterns", 0)
            return [result.get("top_universal_pattern", ""), result.get("top_calibrated_pattern", "")]
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return []

    def get_calibration(self) -> dict:
        """Return real calibration statistics from PatternVault."""
        try:
            from vault import PatternVault
            pv = PatternVault()
            return pv.get_calibration_status()
        except Exception:
            return {"total_scored": 0, "patterns_found": 0, "calibration_accuracy": 0, "status": "not_ready"}

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "patterns_found": self.patterns_found,
        }
