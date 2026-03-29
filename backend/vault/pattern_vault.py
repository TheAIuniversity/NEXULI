"""
Pattern Vault — the central intelligence that learns from every scored piece of content.

Data separation contract (enforced throughout):

  source="own"        — your content. Feeds universal + calibrated analysis.
                        Real metrics from own content drive weight updates.
  source="competitor" — scanned competitor content. Feeds universal +
                        competitor benchmark analysis only. NEVER touches
                        brain learning_weights.
  source="universal"  — explicitly source-agnostic data. Feeds universal
                        analysis only.

Three pattern scopes produced by run_analysis():

  scope="universal"   — ALL good vs ALL bad (cross-source). Brain rules.
  scope="competitor"  — competitor data only. Market benchmarks.
  scope="calibrated"  — own data WITH real metrics. Gold rules. The only
                        patterns that may update brain weights or decide deploys.

Flow:
1. Content scored through TRIBE → record_score(source=...) → stored as example
2. run_analysis() → three separate extractions → patterns stamped with scope
3. Playbook generator organises patterns per scope into playbooks
4. Creative agent reads calibrated playbooks when generating new content
5. Learner agent calls update_brain_weights() → uses calibrated patterns only
6. New content scored → cycle repeats → patterns get more accurate
"""

import json
import logging
import time
from typing import List, Optional

from config import settings

from .example_store import ExampleStore
from .pattern_extractor import Pattern, PatternExtractor
from .playbook_generator import Playbook, PlaybookGenerator

logger = logging.getLogger(__name__)

PATTERNS_PATH = settings.db_path.parent / "patterns.json"
PLAYBOOKS_PATH = settings.db_path.parent / "playbooks.json"

# Minimum calibrated samples before weight updates are permitted
CALIBRATION_READINESS_THRESHOLD = 20
# Minimum for high-confidence weight updates
CALIBRATION_HIGH_CONFIDENCE_THRESHOLD = 50


class PatternVault:
    """Main interface for the pattern-learning vault system."""

    def __init__(self):
        self.examples = ExampleStore()
        self.extractor = PatternExtractor()
        self.playbook_gen = PlaybookGenerator()
        self._patterns: List[Pattern] = []
        self._playbooks: List[Playbook] = []
        self._load_cached()

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load_cached(self) -> None:
        """Load cached patterns and playbooks from disk."""
        if PATTERNS_PATH.exists():
            try:
                data = json.loads(PATTERNS_PATH.read_text())
                self._patterns = [Pattern(**p) for p in data]
            except Exception as exc:
                logger.warning(f"Could not load cached patterns: {exc}")

        if PLAYBOOKS_PATH.exists():
            try:
                data = json.loads(PLAYBOOKS_PATH.read_text())
                self._playbooks = [
                    Playbook(**{k: v for k, v in p.items() if k != "rule_count"})
                    for p in data
                ]
            except Exception as exc:
                logger.warning(f"Could not load cached playbooks: {exc}")

    def _save_patterns(self) -> None:
        PATTERNS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PATTERNS_PATH.write_text(
            json.dumps([p.to_dict() for p in self._patterns], indent=2)
        )

    def _save_playbooks(self) -> None:
        PLAYBOOKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PLAYBOOKS_PATH.write_text(
            json.dumps([p.to_dict() for p in self._playbooks], indent=2)
        )

    # ── Store ────────────────────────────────────────────────────────────────

    def record_score(
        self,
        score_result: dict,
        filename: str = "",
        modality: str = "",
        platform: str = "",
        audience_segment: str = "",
        tags: str = "",
        source: str = "own",
    ):
        """Record a new scored example.

        Args:
            source: Data origin — "own", "competitor", or "universal".
                    This MUST be set correctly. It controls which analysis
                    pools this data point joins and whether it can ever
                    influence brain weight updates.

        Returns:
            The stored ScoredExample.
        """
        example = self.examples.add(
            score_result,
            filename,
            modality,
            platform,
            audience_segment,
            tags,
            source=source,
        )
        logger.info(
            f"Vault: recorded {filename} as {example.classification} "
            f"(score: {example.overall_score}, source: {source})"
        )
        return example

    def add_real_metrics(
        self,
        example_id: str,
        ctr: float = None,
        conversion: float = None,
        watch_time: float = None,
    ) -> None:
        """Add real-world performance data to a stored example.

        Only own-source examples should receive real metrics.
        This method does not enforce that constraint here (the caller knows
        the provenance), but auditing via get_calibration_status() will
        reflect the true state.
        """
        self.examples.update_real_metrics(example_id, ctr, conversion, watch_time)

    # ── Analyse ──────────────────────────────────────────────────────────────

    def run_analysis(self) -> dict:
        """Run three separate pattern extractions enforcing data separation.

        1. Universal patterns — ALL good vs ALL bad (own + competitor).
           Produces brain-level perceptual rules.

        2. Competitor benchmarks — competitor data only.
           Produces market benchmark and gap patterns.

        3. Calibrated patterns — own data WITH real metrics only.
           Produces niche-specific deploy rules and drives weight updates.

        All patterns are stamped with their scope and persisted.
        Returns a summary dict.
        """
        all_patterns: List[Pattern] = []
        summary: dict = {}

        # ── 1. Universal ────────────────────────────────────────────────────
        universal_good = self.examples.get_good(limit=500)
        universal_bad = self.examples.get_bad(limit=500)
        universal_patterns = self.extractor.extract_all(
            universal_good, universal_bad, scope="universal"
        )
        all_patterns.extend(universal_patterns)
        summary["universal"] = {
            "good_examples": len(universal_good),
            "bad_examples": len(universal_bad),
            "patterns_found": len(universal_patterns),
            "proven": sum(1 for p in universal_patterns if p.status == "proven"),
        }
        logger.info(
            f"Universal analysis: {len(universal_patterns)} patterns from "
            f"{len(universal_good)}G/{len(universal_bad)}B examples"
        )

        # ── 2. Competitor benchmarks ────────────────────────────────────────
        competitor_good = self.examples.get_competitor("GOOD", limit=300)
        competitor_bad = self.examples.get_competitor("BAD", limit=300)
        competitor_patterns = self.extractor.extract_all(
            competitor_good, competitor_bad, scope="competitor"
        )
        all_patterns.extend(competitor_patterns)
        summary["competitor"] = {
            "good_examples": len(competitor_good),
            "bad_examples": len(competitor_bad),
            "patterns_found": len(competitor_patterns),
            "proven": sum(1 for p in competitor_patterns if p.status == "proven"),
        }
        logger.info(
            f"Competitor analysis: {len(competitor_patterns)} patterns from "
            f"{len(competitor_good)}G/{len(competitor_bad)}B competitor examples"
        )

        # ── 3. Calibrated (own + real metrics) ─────────────────────────────
        calibrated_rows = self.examples.get_calibrated(limit=300)
        # Split into good/bad using the stored classification
        calibrated_good = [r for r in calibrated_rows if r["classification"] == "GOOD"]
        calibrated_bad = [r for r in calibrated_rows if r["classification"] == "BAD"]
        calibrated_patterns = self.extractor.extract_all(
            calibrated_good, calibrated_bad, scope="calibrated"
        )
        all_patterns.extend(calibrated_patterns)
        cal_status = self.get_calibration_status()
        summary["calibrated"] = {
            "total_calibrated": len(calibrated_rows),
            "good_examples": len(calibrated_good),
            "bad_examples": len(calibrated_bad),
            "patterns_found": len(calibrated_patterns),
            "proven": sum(1 for p in calibrated_patterns if p.status == "proven"),
            "readiness_pct": cal_status["readiness_pct"],
        }
        logger.info(
            f"Calibrated analysis: {len(calibrated_patterns)} patterns from "
            f"{len(calibrated_rows)} calibrated own examples"
        )

        self._patterns = all_patterns
        self._save_patterns()

        # Generate playbooks per scope
        self._playbooks = self.playbook_gen.generate_all(
            self._patterns, scope="all"
        )
        self._save_playbooks()

        summary["total_patterns"] = len(all_patterns)
        summary["total_playbooks"] = len(self._playbooks)
        summary["top_universal_pattern"] = (
            next(
                (p.pattern for p in all_patterns if p.scope == "universal"),
                "Not enough data yet",
            )
        )
        summary["top_calibrated_pattern"] = (
            next(
                (p.pattern for p in all_patterns if p.scope == "calibrated"),
                "Not enough calibrated data yet",
            )
        )
        return summary

    # ── Query ────────────────────────────────────────────────────────────────

    def get_patterns(
        self,
        status: str = None,
        category: str = None,
        scope: str = None,
    ) -> List[dict]:
        """Get discovered patterns, optionally filtered by status, category, or scope."""
        result = self._patterns
        if status:
            result = [p for p in result if p.status == status]
        if category:
            result = [p for p in result if p.category == category]
        if scope:
            result = [p for p in result if p.scope == scope]
        return [p.to_dict() for p in result]

    def get_playbooks(self) -> List[dict]:
        """Get all generated playbooks."""
        return [p.to_dict() for p in self._playbooks]

    def get_playbook(self, name: str) -> Optional[dict]:
        """Get a specific playbook by name."""
        for p in self._playbooks:
            if p.name == name:
                return p.to_dict()
        return None

    def get_examples(
        self,
        classification: str = None,
        source: str = None,
        limit: int = 100,
    ) -> List[dict]:
        """Get stored examples, optionally filtered by classification and/or source."""
        return self.examples.get_all(classification, source, limit)

    def get_stats(self) -> dict:
        """Get vault statistics including per-scope pattern breakdown."""
        example_stats = self.examples.get_stats()

        by_scope: dict = {}
        for p in self._patterns:
            scope = p.scope
            if scope not in by_scope:
                by_scope[scope] = {"total": 0, "proven": 0, "emerging": 0}
            by_scope[scope]["total"] += 1
            if p.status == "proven":
                by_scope[scope]["proven"] += 1
            elif p.status == "emerging":
                by_scope[scope]["emerging"] += 1

        proven = sum(1 for p in self._patterns if p.status == "proven")
        emerging = sum(1 for p in self._patterns if p.status == "emerging")

        return {
            "examples": example_stats,
            "patterns": {
                "total": len(self._patterns),
                "proven": proven,
                "emerging": emerging,
                "by_scope": by_scope,
                "categories": list({p.category for p in self._patterns}),
            },
            "playbooks": {
                "count": len(self._playbooks),
                "names": [p.name for p in self._playbooks],
            },
            "calibration": self.get_calibration_status(),
        }

    def get_creative_guidelines(self, scope: str = None) -> dict:
        """Return creative guidelines organised by scope.

        Args:
            scope: If supplied, returns guidelines for that scope only
                   ("universal", "competitor", "calibrated").
                   If None, returns all scopes grouped.

        The creative agent should prefer calibrated guidelines when available,
        fall back to universal, and treat competitor guidelines as reference only.
        """
        scopes_to_include = (
            [scope] if scope else ["calibrated", "universal", "competitor"]
        )

        result: dict = {"status": "active", "by_scope": {}}
        any_data = False

        for s in scopes_to_include:
            scope_patterns = [p for p in self._patterns if p.scope == s]
            usable = [
                p for p in scope_patterns
                if p.status == "proven" or p.confidence >= 0.5
            ]
            if not usable:
                result["by_scope"][s] = {
                    "status": "insufficient_data",
                    "guidelines": [],
                }
                continue

            any_data = True
            guidelines = [
                {
                    "rule": p.pattern,
                    "impact": p.estimated_score_impact,
                    "confidence": p.confidence,
                    "category": p.category,
                    "scope": p.scope,
                }
                for p in sorted(
                    usable, key=lambda x: x.estimated_score_impact, reverse=True
                )[:10]
            ]
            result["by_scope"][s] = {
                "status": "active",
                "guidelines": guidelines,
                "pattern_count": len(usable),
            }

        if not any_data:
            result["status"] = "insufficient_data"
            result["message"] = "Score more content to discover patterns."

        result["based_on"] = f"{self.examples.get_stats()['total']} scored examples"
        return result

    # ── Calibration ──────────────────────────────────────────────────────────

    def get_calibration_status(self) -> dict:
        """Return how many own samples have real metrics and readiness percentage.

        Readiness is measured against CALIBRATION_HIGH_CONFIDENCE_THRESHOLD (50).
        Below CALIBRATION_READINESS_THRESHOLD (20) → not ready.
        20-49 → partially ready (use with caution warning).
        50+ → fully calibrated.
        """
        stats = self.examples.get_stats()
        own_total = stats["by_source"]["own"]
        calibrated = stats["calibrated"]

        readiness_pct = min(
            100,
            round((calibrated / CALIBRATION_HIGH_CONFIDENCE_THRESHOLD) * 100, 1),
        )

        if calibrated < CALIBRATION_READINESS_THRESHOLD:
            status = "not_ready"
            message = (
                f"Need {CALIBRATION_READINESS_THRESHOLD - calibrated} more own examples "
                f"with real metrics before calibration is usable."
            )
        elif calibrated < CALIBRATION_HIGH_CONFIDENCE_THRESHOLD:
            status = "partial"
            message = (
                f"{calibrated} calibrated samples. Patterns exist but confidence is low. "
                f"Target {CALIBRATION_HIGH_CONFIDENCE_THRESHOLD} for high confidence."
            )
        else:
            status = "calibrated"
            message = (
                f"{calibrated} calibrated samples. Full calibration active."
            )

        calibrated_patterns = [p for p in self._patterns if p.scope == "calibrated"]

        return {
            "status": status,
            "own_total": own_total,
            "calibrated_samples": calibrated,
            "readiness_pct": readiness_pct,
            "calibrated_patterns": len(calibrated_patterns),
            "proven_calibrated_patterns": sum(
                1 for p in calibrated_patterns if p.status == "proven"
            ),
            "message": message,
            "weight_updates_allowed": calibrated >= CALIBRATION_READINESS_THRESHOLD,
        }

    # ── Brain weight update (calibrated data only) ───────────────────────────

    def update_brain_weights(self) -> dict:
        """Update AgentBrain learning_weights using ONLY calibrated patterns.

        Rules:
        - Never reads competitor or universal patterns for weight decisions.
        - Requires minimum calibrated samples (CALIBRATION_READINESS_THRESHOLD).
        - Adjusts weights based on Pearson r correlations discovered in
          _calibration_patterns(): regions with high positive correlation to
          real CTR/conversion get higher weights; negative or weak correlation
          get lower weights.

        Returns a summary of what was updated.
        """
        from intelligence.brain import AgentBrain

        cal_status = self.get_calibration_status()

        if not cal_status["weight_updates_allowed"]:
            msg = (
                f"Weight update skipped: only {cal_status['calibrated_samples']} "
                f"calibrated samples, need {CALIBRATION_READINESS_THRESHOLD}."
            )
            logger.info(msg)
            return {"updated": False, "reason": msg, "calibration": cal_status}

        # Gather calibrated patterns with correlation detail
        cal_patterns = [
            p for p in self._patterns
            if p.scope == "calibrated"
            and p.category == "calibration"
            and p.calibration_detail is not None
        ]

        if not cal_patterns:
            msg = "Weight update skipped: no calibration-category patterns available yet."
            logger.info(msg)
            return {"updated": False, "reason": msg, "calibration": cal_status}

        brain = AgentBrain.get()
        weights = brain.weights

        # Map region_key → weight_key
        region_to_weight = {
            "decision_avg": "prefrontal",
            "visual_avg": "visual_cortex",
            "auditory_avg": "auditory_cortex",
            "language_avg": "language_areas",
            "emotion_avg": "default_mode",
            "hook_score": "hook_strength",
        }

        # Aggregate correlations per region across all real metrics
        # We use a weighted average (weight = n_samples)
        region_corr_sum: dict = {}
        region_corr_weight: dict = {}

        for p in cal_patterns:
            detail = p.calibration_detail
            region_key = detail.get("region_key", "")
            weight_key = region_to_weight.get(region_key)
            if weight_key is None:
                continue
            corr = detail.get("correlation", 0)
            n = detail.get("n_samples", 1)
            region_corr_sum[weight_key] = region_corr_sum.get(weight_key, 0) + corr * n
            region_corr_weight[weight_key] = region_corr_weight.get(weight_key, 0) + n

        learning_rate = 0.1
        updates_made = {}

        for weight_key, corr_sum in region_corr_sum.items():
            total_n = region_corr_weight[weight_key]
            avg_corr = corr_sum / total_n  # weighted average correlation

            old_weight = weights.get(weight_key, 1.0)
            # Positive correlation → increase weight; negative → decrease
            delta = learning_rate * avg_corr
            new_weight = max(0.1, min(5.0, old_weight + delta))
            weights[weight_key] = round(new_weight, 4)
            updates_made[weight_key] = {
                "old": round(old_weight, 4),
                "new": round(new_weight, 4),
                "avg_correlation": round(avg_corr, 4),
                "n_samples": total_n,
            }

        # Persist the updated weights back through the brain's save mechanism
        brain._data["learning_weights"] = weights
        brain._save()

        logger.info(
            f"Brain weights updated from {len(cal_patterns)} calibrated patterns. "
            f"Regions adjusted: {list(updates_made.keys())}"
        )

        return {
            "updated": True,
            "calibrated_patterns_used": len(cal_patterns),
            "calibrated_samples": cal_status["calibrated_samples"],
            "weight_changes": updates_made,
        }
