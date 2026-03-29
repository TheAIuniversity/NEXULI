"""
Playbook Generator — converts proven patterns into actionable creative rules.

Scope-aware generation:

  Universal playbooks  — Hook Rules, Brain Activation Rules, etc.
                         Drawn from scope="universal" patterns.
                         Apply to all content creation.

  Competitor playbooks — Market Benchmark, Competitor Gaps.
                         Drawn from scope="competitor" patterns.
                         Reference only; do not inform weight updates.

  Calibrated playbooks — "Niche Playbook" (the money).
                         Drawn ONLY from scope="calibrated" patterns.
                         These are niche-specific, proven-by-real-data rules
                         that should govern deploy decisions.
                         Carries a confidence warning if < 50 calibrated samples.

The generate_all() API is backward-compatible: passing scope="all" (default)
generates all three families. Pass scope="universal", "competitor", or
"calibrated" to generate just that family.
"""

import time
import logging
from typing import List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Calibration warning threshold — mirrors PatternVault constant
NICHE_PLAYBOOK_WARNING_THRESHOLD = 50


@dataclass
class PlaybookRule:
    rule: str
    source_pattern_id: str
    confidence: float
    impact: float
    category: str
    evidence: str  # "Based on X good vs Y bad examples"
    scope: str = "universal"


@dataclass
class Playbook:
    name: str
    description: str
    scope: str = "universal"  # "universal" | "competitor" | "calibrated" | "master"
    rules: List[PlaybookRule] = field(default_factory=list)
    generated_at: float = 0
    warning: Optional[str] = None  # set when confidence is low

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "rules": [
                {
                    "rule": r.rule,
                    "confidence": round(r.confidence, 2),
                    "impact": round(r.impact, 1),
                    "category": r.category,
                    "evidence": r.evidence,
                    "scope": r.scope,
                }
                for r in self.rules
            ],
            "generated_at": self.generated_at,
            "rule_count": len(self.rules),
        }
        if self.warning:
            d["warning"] = self.warning
        return d


class PlaybookGenerator:
    """Generates scope-segregated playbooks from proven patterns."""

    # ── Universal playbook names ──────────────────────────────────────────
    _UNIVERSAL_CATEGORY_NAMES = {
        "hook": (
            "Hook Rules",
            "Universal rules for the first 3 seconds — derived from all scored content",
        ),
        "modality": (
            "Modality Mix Rules",
            "Which channels (visual/audio/text) to prioritize — universal signal",
        ),
        "region": (
            "Brain Activation Rules",
            "Which brain regions to target and how — universal perceptual rules",
        ),
        "structure": (
            "Content Structure Rules",
            "How to structure content for sustained engagement — universal",
        ),
        "timing": (
            "Timing Rules",
            "When to place key moments for maximum impact — universal",
        ),
    }

    # ── Competitor playbook names ─────────────────────────────────────────
    _COMPETITOR_CATEGORY_NAMES = {
        "hook": (
            "Market Benchmark — Hook",
            "How top competitor hooks compare to weak ones in your market",
        ),
        "modality": (
            "Market Benchmark — Modality Mix",
            "Modality patterns that separate top from bottom competitor content",
        ),
        "region": (
            "Market Benchmark — Brain Activation",
            "Brain region activation patterns in competitor content",
        ),
        "structure": (
            "Competitor Gaps — Structure",
            "Structural weaknesses and strengths in competitor content",
        ),
        "timing": (
            "Competitor Gaps — Timing",
            "Timing patterns observed in competitor content",
        ),
    }

    def generate_all(self, patterns: list, scope: str = "all") -> List[Playbook]:
        """Generate playbooks organised by scope and category.

        Args:
            patterns: All Pattern objects (may be mixed scope).
            scope:    "all"        — generate all three families (default).
                      "universal"  — universal playbooks only.
                      "competitor" — competitor playbooks only.
                      "calibrated" — calibrated (Niche) playbook only.

        Returns:
            List of Playbook objects. Universal and calibrated families each
            get a Master Playbook that ranks rules by impact. Competitor family
            gets a "Market Overview" master.
        """
        valid_scopes = {"all", "universal", "competitor", "calibrated"}
        if scope not in valid_scopes:
            raise ValueError(f"Invalid scope '{scope}'. Must be one of: {valid_scopes}")

        playbooks: List[Playbook] = []

        if scope in ("all", "universal"):
            playbooks.extend(
                self._generate_universal(
                    [p for p in patterns if p.scope == "universal"]
                )
            )

        if scope in ("all", "competitor"):
            playbooks.extend(
                self._generate_competitor(
                    [p for p in patterns if p.scope == "competitor"]
                )
            )

        if scope in ("all", "calibrated"):
            niche = self._generate_calibrated(
                [p for p in patterns if p.scope == "calibrated"]
            )
            if niche:
                playbooks.extend(niche)

        return playbooks

    # ── Universal ────────────────────────────────────────────────────────

    def _generate_universal(self, patterns: list) -> List[Playbook]:
        """Generate universal playbooks (one per category + master)."""
        strong = [
            p for p in patterns
            if p.confidence >= 0.5 and p.total_examples >= 5
        ]
        if not strong:
            return []

        by_category = self._group_by_category(strong)
        playbooks: List[Playbook] = []

        for category, pats in by_category.items():
            name, desc = self._UNIVERSAL_CATEGORY_NAMES.get(
                category,
                (f"{category.title()} Rules", f"Universal {category} patterns"),
            )
            rules = self._make_rules(pats, scope="universal")
            playbooks.append(
                Playbook(
                    name=name,
                    description=desc,
                    scope="universal",
                    rules=rules,
                    generated_at=time.time(),
                )
            )

        # Master universal playbook
        all_rules = self._collect_and_rank_rules(playbooks)
        if all_rules:
            playbooks.insert(
                0,
                Playbook(
                    name="Master Playbook",
                    description=(
                        "Top universal rules across all categories, ranked by score impact. "
                        "Applies to all content regardless of niche."
                    ),
                    scope="universal",
                    rules=all_rules[:15],
                    generated_at=time.time(),
                ),
            )

        return playbooks

    # ── Competitor ───────────────────────────────────────────────────────

    def _generate_competitor(self, patterns: list) -> List[Playbook]:
        """Generate competitor benchmark playbooks."""
        strong = [
            p for p in patterns
            if p.confidence >= 0.5 and p.total_examples >= 5
        ]
        if not strong:
            return []

        by_category = self._group_by_category(strong)
        playbooks: List[Playbook] = []

        for category, pats in by_category.items():
            name, desc = self._COMPETITOR_CATEGORY_NAMES.get(
                category,
                (
                    f"Competitor Benchmark — {category.title()}",
                    f"Competitor patterns for {category}",
                ),
            )
            rules = self._make_rules(pats, scope="competitor")
            playbooks.append(
                Playbook(
                    name=name,
                    description=desc,
                    scope="competitor",
                    rules=rules,
                    generated_at=time.time(),
                )
            )

        # Market overview master
        all_rules = self._collect_and_rank_rules(playbooks)
        if all_rules:
            playbooks.insert(
                0,
                Playbook(
                    name="Market Overview Playbook",
                    description=(
                        "Top competitor patterns ranked by impact. "
                        "For reference and gap analysis only — never used for weight updates."
                    ),
                    scope="competitor",
                    rules=all_rules[:15],
                    generated_at=time.time(),
                ),
            )

        return playbooks

    # ── Calibrated (Niche) ───────────────────────────────────────────────

    def _generate_calibrated(self, patterns: list) -> List[Playbook]:
        """Generate the Niche Playbook from calibrated own data patterns.

        This is the highest-value playbook: rules derived exclusively from
        your own content with real performance data attached.

        Includes a low-confidence warning when the calibrated sample count
        is below NICHE_PLAYBOOK_WARNING_THRESHOLD (50).
        """
        if not patterns:
            return []

        # Determine total calibrated sample count from the patterns themselves
        # Use the maximum total_examples across patterns as a proxy
        max_samples = max((p.total_examples for p in patterns), default=0)

        warning: Optional[str] = None
        if max_samples < NICHE_PLAYBOOK_WARNING_THRESHOLD:
            warning = (
                f"LOW CONFIDENCE WARNING: Niche Playbook is based on only "
                f"{max_samples} calibrated samples. "
                f"Rules may be unreliable. "
                f"Target {NICHE_PLAYBOOK_WARNING_THRESHOLD} samples for high confidence. "
                f"Do not use for deploy decisions until this threshold is met."
            )
            logger.warning(f"Niche Playbook generated with warning: {warning}")

        strong = [
            p for p in patterns
            if p.confidence >= 0.4 and p.total_examples >= 3
        ]
        if not strong:
            return []

        # Separate general structural patterns from calibration correlations
        calibration_pats = [p for p in strong if p.category == "calibration"]
        other_pats = [p for p in strong if p.category != "calibration"]

        playbooks: List[Playbook] = []

        # Main Niche Playbook
        all_rules = self._make_rules(
            sorted(strong, key=lambda p: p.estimated_score_impact, reverse=True),
            scope="calibrated",
        )
        playbooks.append(
            Playbook(
                name="Niche Playbook",
                description=(
                    "Rules discovered exclusively from your own content with real "
                    "performance data. These govern deploy decisions and brain weight "
                    "updates. More valuable than any universal or competitor pattern."
                ),
                scope="calibrated",
                rules=all_rules[:20],
                generated_at=time.time(),
                warning=warning,
            )
        )

        # Correlation sub-playbook (the actual TRIBE→real-world mappings)
        if calibration_pats:
            corr_rules = self._make_rules(
                sorted(calibration_pats, key=lambda p: p.confidence, reverse=True),
                scope="calibrated",
            )
            playbooks.append(
                Playbook(
                    name="Score-to-Performance Correlations",
                    description=(
                        "Direct correlations between TRIBE brain scores and real CTR / "
                        "conversion / watch time in your niche. "
                        "These are what the weight updater reads."
                    ),
                    scope="calibrated",
                    rules=corr_rules,
                    generated_at=time.time(),
                    warning=warning,
                )
            )

        return playbooks

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _group_by_category(patterns: list) -> dict:
        by_category: dict = {}
        for p in patterns:
            by_category.setdefault(p.category, []).append(p)
        return by_category

    @staticmethod
    def _make_rules(patterns: list, scope: str) -> List[PlaybookRule]:
        return [
            PlaybookRule(
                rule=p.pattern,
                source_pattern_id=p.id,
                confidence=p.confidence,
                impact=p.estimated_score_impact,
                category=p.category,
                evidence=(
                    f"Based on {p.good_examples} good vs {p.bad_examples} bad examples"
                ),
                scope=scope,
            )
            for p in sorted(
                patterns, key=lambda x: x.estimated_score_impact, reverse=True
            )
        ]

    @staticmethod
    def _collect_and_rank_rules(playbooks: List[Playbook]) -> List[PlaybookRule]:
        all_rules: List[PlaybookRule] = []
        for pb in playbooks:
            all_rules.extend(pb.rules)
        all_rules.sort(key=lambda r: r.impact, reverse=True)
        return all_rules
