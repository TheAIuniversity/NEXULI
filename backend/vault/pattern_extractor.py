"""
Pattern Extractor — discovers what makes content GOOD vs BAD from scored examples.

Three analysis scopes with strict data separation:

  scope="universal"   — ALL good vs ALL bad (own + competitor combined).
                        Produces brain-level perceptual rules that apply
                        regardless of niche. Fed into brain.patterns but
                        NEVER used to update learning_weights.

  scope="competitor"  — competitor data only. Produces benchmark patterns:
                        "top competitor hooks average 82, market average 61."
                        Used for gap analysis, never for weight updates.

  scope="calibrated"  — own data WITH real metrics only. These are the gold
                        patterns: TRIBE scores correlated with real CTR /
                        conversion / watch_time. The ONLY source for weight
                        updates and deploy decisions.
"""

import json
import time
import logging
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

VALID_SCOPES = {"universal", "competitor", "calibrated"}


@dataclass
class Pattern:
    id: str
    pattern: str  # human-readable description
    category: str  # hook, modality, region, timing, structure, calibration
    status: str  # proven (>10 examples, >70% confidence), emerging (3-10), weak

    # Evidence
    confidence: float  # 0-1
    good_examples: int  # how many GOOD examples show this
    bad_examples: int  # how many BAD examples show this
    total_examples: int

    # Quantitative
    good_avg: float  # average value in GOOD examples
    bad_avg: float  # average value in BAD examples
    delta_pct: float  # percentage difference

    # Impact
    estimated_score_impact: float  # how many score points this pattern is worth

    # Data origin — which pool this pattern was discovered in
    scope: str = "universal"  # "universal" | "competitor" | "calibrated"

    discovered_at: float = 0
    last_confirmed: float = 0

    # Calibration-specific: real metric correlation
    # e.g. {"metric": "real_ctr", "correlation": 0.82, "threshold": 70}
    calibration_detail: Optional[dict] = field(default=None)

    def to_dict(self) -> dict:
        return asdict(self)


class PatternExtractor:
    """Extracts patterns from scored examples with scope-aware data separation."""

    def extract_all(
        self,
        good_examples: List[dict],
        bad_examples: List[dict],
        scope: str = "universal",
    ) -> List[Pattern]:
        """Run all pattern extraction on GOOD vs BAD examples for a given scope.

        Args:
            good_examples: Pre-filtered GOOD examples for this scope.
            bad_examples:  Pre-filtered BAD examples for this scope.
            scope:         One of "universal", "competitor", "calibrated".
                           Every returned Pattern carries this scope value.

        Returns:
            List of discovered patterns sorted by confidence, each stamped
            with the supplied scope.
        """
        if scope not in VALID_SCOPES:
            raise ValueError(
                f"Invalid scope '{scope}'. Must be one of: {VALID_SCOPES}"
            )

        if len(good_examples) < 3 or len(bad_examples) < 3:
            logger.info(
                f"[scope={scope}] Not enough examples "
                f"(good: {len(good_examples)}, bad: {len(bad_examples)}). Need 3+ each."
            )
            return []

        patterns: List[Pattern] = []
        patterns.extend(self._hook_patterns(good_examples, bad_examples, scope))
        patterns.extend(self._modality_patterns(good_examples, bad_examples, scope))
        patterns.extend(self._region_patterns(good_examples, bad_examples, scope))
        patterns.extend(self._structure_patterns(good_examples, bad_examples, scope))
        patterns.extend(self._timing_patterns(good_examples, bad_examples, scope))

        # Calibrated scope gets additional correlation analysis
        if scope == "calibrated":
            patterns.extend(self._calibration_patterns(good_examples, bad_examples))

        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)

        # Assign status
        for p in patterns:
            total = p.good_examples + p.bad_examples
            if total >= 10 and p.confidence >= 0.70:
                p.status = "proven"
            elif total >= 3:
                p.status = "emerging"
            else:
                p.status = "weak"

        proven_count = sum(1 for p in patterns if p.status == "proven")
        logger.info(
            f"[scope={scope}] Extracted {len(patterns)} patterns ({proven_count} proven)"
        )
        return patterns

    # ── Calibration patterns (own data + real metrics only) ────────────────

    def _calibration_patterns(
        self,
        own_good: List[dict],
        own_bad: List[dict],
    ) -> List[Pattern]:
        """Correlate TRIBE region scores with real-world performance metrics.

        These patterns answer: "does a high prefrontal score actually predict
        CTR in our niche?" They are the authoritative source for weight updates.

        Only examples with at least one real metric are usable here; the caller
        is expected to pass only calibrated rows (source='own' + has metrics),
        but this method filters defensively.

        Patterns produced have category="calibration" and scope="calibrated".
        """
        patterns: List[Pattern] = []
        all_examples = own_good + own_bad

        # Keep only rows that actually have real metrics
        with_ctr = [e for e in all_examples if e.get("real_ctr") is not None]
        with_conv = [e for e in all_examples if e.get("real_conversion") is not None]
        with_wt = [e for e in all_examples if e.get("real_watch_time") is not None]

        region_map = {
            "prefrontal (decision)": "decision_avg",
            "visual cortex": "visual_avg",
            "auditory cortex": "auditory_avg",
            "language areas": "language_avg",
            "default mode (emotion)": "emotion_avg",
            "hook strength": "hook_score",
        }

        metric_configs = [
            ("CTR", "real_ctr", with_ctr, "C"),
            ("conversion rate", "real_conversion", with_conv, "V"),
            ("watch time", "real_watch_time", with_wt, "W"),
        ]

        pattern_idx = 1
        for metric_label, metric_key, subset, prefix in metric_configs:
            if len(subset) < 5:
                # Need minimum 5 calibrated samples per metric to be meaningful
                continue

            for region_label, score_key in region_map.items():
                region_vals = [e.get(score_key, 0) or 0 for e in subset]
                metric_vals = [e.get(metric_key, 0) or 0 for e in subset]

                if not region_vals or not metric_vals:
                    continue

                corr = self._pearson(region_vals, metric_vals)
                if corr is None or abs(corr) < 0.3:
                    continue  # Not interesting enough

                region_arr = np.array(region_vals)
                metric_arr = np.array(metric_vals)

                # Find a natural threshold: mean of the region scores
                threshold = float(np.mean(region_arr))

                above_mask = region_arr >= threshold
                below_mask = ~above_mask

                above_metric = (
                    float(np.mean(metric_arr[above_mask])) if above_mask.any() else 0
                )
                below_metric = (
                    float(np.mean(metric_arr[below_mask])) if below_mask.any() else 0
                )

                direction = "positively" if corr > 0 else "negatively"
                pid = f"CAL-{prefix}{pattern_idx:03d}"
                pattern_idx += 1

                patterns.append(
                    Pattern(
                        id=pid,
                        pattern=(
                            f"{region_label} score {direction} correlates with "
                            f"{metric_label} (r={corr:+.2f}): "
                            f"above {threshold:.0f} avg {metric_label}={above_metric:.3f}, "
                            f"below {threshold:.0f} avg {metric_label}={below_metric:.3f}"
                        ),
                        category="calibration",
                        status="emerging",
                        scope="calibrated",
                        confidence=round(min(0.99, abs(corr)), 3),
                        good_examples=int(above_mask.sum()),
                        bad_examples=int(below_mask.sum()),
                        total_examples=len(subset),
                        good_avg=round(above_metric, 4),
                        bad_avg=round(below_metric, 4),
                        delta_pct=round(
                            ((above_metric - below_metric) / max(below_metric, 0.0001))
                            * 100,
                            1,
                        ),
                        estimated_score_impact=round(abs(corr) * 10, 1),
                        discovered_at=time.time(),
                        last_confirmed=time.time(),
                        calibration_detail={
                            "metric": metric_key,
                            "correlation": round(float(corr), 4),
                            "threshold": round(threshold, 1),
                            "region_key": score_key,
                            "n_samples": len(subset),
                        },
                    )
                )

        return patterns

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _pearson(x: list, y: list) -> Optional[float]:
        """Return Pearson r, or None if it cannot be computed."""
        if len(x) < 3 or len(y) < 3:
            return None
        x_arr = np.array(x, dtype=float)
        y_arr = np.array(y, dtype=float)
        if x_arr.std() == 0 or y_arr.std() == 0:
            return None
        return float(np.corrcoef(x_arr, y_arr)[0, 1])

    def _compare_metric(
        self, good: List[dict], bad: List[dict], key: str
    ) -> Tuple[float, float, float, float]:
        """Compare a metric between good and bad examples.

        Returns (good_avg, bad_avg, delta_pct, confidence).
        """
        good_vals = [e.get(key, 0) or 0 for e in good]
        bad_vals = [e.get(key, 0) or 0 for e in bad]

        good_avg = float(np.mean(good_vals)) if good_vals else 0.0
        bad_avg = float(np.mean(bad_vals)) if bad_vals else 0.0

        if bad_avg > 0:
            delta_pct = ((good_avg - bad_avg) / bad_avg) * 100
        elif good_avg > 0:
            delta_pct = 100.0
        else:
            delta_pct = 0.0

        # Confidence based on effect size + sample size
        if len(good_vals) > 1 and len(bad_vals) > 1:
            good_std = float(np.std(good_vals))
            bad_std = float(np.std(bad_vals))
            pooled_std = np.sqrt((good_std**2 + bad_std**2) / 2)
            if pooled_std > 0:
                effect_size = abs(good_avg - bad_avg) / pooled_std
                n = min(len(good_vals), len(bad_vals))
                confidence = min(0.99, 1 - 1 / (1 + effect_size * np.sqrt(n / 2)))
            else:
                confidence = 0.5
        else:
            confidence = 0.3

        return good_avg, bad_avg, float(delta_pct), float(confidence)

    def _make_pattern(
        self,
        pid: str,
        text: str,
        category: str,
        good_avg: float,
        bad_avg: float,
        delta_pct: float,
        confidence: float,
        good_count: int,
        bad_count: int,
        scope: str = "universal",
    ) -> Pattern:
        return Pattern(
            id=pid,
            pattern=text,
            category=category,
            status="emerging",
            scope=scope,
            confidence=round(confidence, 3),
            good_examples=good_count,
            bad_examples=bad_count,
            total_examples=good_count + bad_count,
            good_avg=round(good_avg, 1),
            bad_avg=round(bad_avg, 1),
            delta_pct=round(delta_pct, 1),
            estimated_score_impact=round(abs(good_avg - bad_avg) * confidence, 1),
            discovered_at=time.time(),
            last_confirmed=time.time(),
        )

    # ── Standard extraction methods (scope-aware wrappers) ─────────────────

    def _hook_patterns(
        self, good: List[dict], bad: List[dict], scope: str
    ) -> List[Pattern]:
        patterns = []
        g_avg, b_avg, delta, conf = self._compare_metric(good, bad, "hook_score")
        if abs(delta) > 10 and conf > 0.4:
            patterns.append(
                self._make_pattern(
                    f"H-001-{scope[:3].upper()}",
                    f"Strong hooks score {delta:+.0f}% higher in top content "
                    f"(good avg: {g_avg:.0f}, bad avg: {b_avg:.0f})",
                    "hook",
                    g_avg,
                    b_avg,
                    delta,
                    conf,
                    len(good),
                    len(bad),
                    scope,
                )
            )
        return patterns

    def _modality_patterns(
        self, good: List[dict], bad: List[dict], scope: str
    ) -> List[Pattern]:
        patterns = []
        checks = [
            ("visual_pct", "visual", f"M-001-{scope[:3].upper()}"),
            ("audio_pct", "audio", f"M-002-{scope[:3].upper()}"),
            ("text_pct", "text", f"M-003-{scope[:3].upper()}"),
        ]
        for metric, name, pid in checks:
            g_avg, b_avg, delta, conf = self._compare_metric(good, bad, metric)
            if abs(delta) > 10 and conf > 0.4:
                direction = "higher" if delta > 0 else "lower"
                patterns.append(
                    self._make_pattern(
                        pid,
                        f"Good content has {abs(delta):.0f}% {direction} {name} contribution "
                        f"(good: {g_avg:.0f}%, bad: {b_avg:.0f}%)",
                        "modality",
                        g_avg,
                        b_avg,
                        delta,
                        conf,
                        len(good),
                        len(bad),
                        scope,
                    )
                )
        return patterns

    def _region_patterns(
        self, good: List[dict], bad: List[dict], scope: str
    ) -> List[Pattern]:
        patterns = []
        checks = [
            ("visual_avg", "visual cortex", f"R-001-{scope[:3].upper()}"),
            ("auditory_avg", "auditory cortex", f"R-002-{scope[:3].upper()}"),
            ("language_avg", "language areas", f"R-003-{scope[:3].upper()}"),
            ("decision_avg", "prefrontal (decision)", f"R-004-{scope[:3].upper()}"),
            ("emotion_avg", "default mode (emotion)", f"R-005-{scope[:3].upper()}"),
        ]
        for metric, name, pid in checks:
            g_avg, b_avg, delta, conf = self._compare_metric(good, bad, metric)
            if abs(delta) > 8 and conf > 0.4:
                patterns.append(
                    self._make_pattern(
                        pid,
                        f"Good content activates {name} {abs(delta):.0f}% more "
                        f"(good: {g_avg:.0f}, bad: {b_avg:.0f})",
                        "region",
                        g_avg,
                        b_avg,
                        delta,
                        conf,
                        len(good),
                        len(bad),
                        scope,
                    )
                )
        return patterns

    def _structure_patterns(
        self, good: List[dict], bad: List[dict], scope: str
    ) -> List[Pattern]:
        patterns = []

        g_avg, b_avg, delta, conf = self._compare_metric(
            good, bad, "weak_moment_count"
        )
        if abs(delta) > 15 and conf > 0.4:
            patterns.append(
                self._make_pattern(
                    f"S-001-{scope[:3].upper()}",
                    f"Good content has {abs(delta):.0f}% fewer weak moments "
                    f"(good: {g_avg:.1f}, bad: {b_avg:.1f})",
                    "structure",
                    g_avg,
                    b_avg,
                    delta,
                    conf,
                    len(good),
                    len(bad),
                    scope,
                )
            )

        g_avg, b_avg, delta, conf = self._compare_metric(
            good, bad, "peak_moment_count"
        )
        if abs(delta) > 15 and conf > 0.4:
            patterns.append(
                self._make_pattern(
                    f"S-002-{scope[:3].upper()}",
                    f"Good content has {abs(delta):.0f}% more peak moments "
                    f"(good: {g_avg:.1f}, bad: {b_avg:.1f})",
                    "structure",
                    g_avg,
                    b_avg,
                    delta,
                    conf,
                    len(good),
                    len(bad),
                    scope,
                )
            )

        return patterns

    def _timing_patterns(
        self, good: List[dict], bad: List[dict], scope: str
    ) -> List[Pattern]:
        """Patterns derived from full_result JSON per-second attention data."""
        patterns = []

        def first_last_ratio(examples: List[dict]) -> List[float]:
            ratios = []
            for ex in examples:
                try:
                    raw = ex.get("full_result", "{}")
                    result = json.loads(raw) if isinstance(raw, str) else raw
                    per_second = result.get("per_second", [])
                    if len(per_second) >= 6:
                        first3 = np.mean(
                            [
                                s["attention"] if isinstance(s, dict) else s
                                for s in per_second[:3]
                            ]
                        )
                        last3 = np.mean(
                            [
                                s["attention"] if isinstance(s, dict) else s
                                for s in per_second[-3:]
                            ]
                        )
                        if last3 > 0:
                            ratios.append(float(first3 / last3))
                except Exception:
                    pass
            return ratios

        good_ratios = first_last_ratio(good)
        bad_ratios = first_last_ratio(bad)

        if good_ratios and bad_ratios:
            g_avg = float(np.mean(good_ratios))
            b_avg = float(np.mean(bad_ratios))
            denominator = max(b_avg, 0.01)

            if g_avg > b_avg * 1.15:
                patterns.append(
                    self._make_pattern(
                        f"T-001-{scope[:3].upper()}",
                        f"Good content front-loads attention "
                        f"(first 3s / last 3s ratio: {g_avg:.2f} vs {b_avg:.2f})",
                        "timing",
                        g_avg,
                        b_avg,
                        ((g_avg - b_avg) / denominator) * 100,
                        0.6,
                        len(good_ratios),
                        len(bad_ratios),
                        scope,
                    )
                )
            elif b_avg > g_avg * 1.15:
                patterns.append(
                    self._make_pattern(
                        f"T-002-{scope[:3].upper()}",
                        f"Good content builds to end "
                        f"(first/last ratio: {g_avg:.2f} vs {b_avg:.2f})",
                        "timing",
                        g_avg,
                        b_avg,
                        ((g_avg - b_avg) / denominator) * 100,
                        0.6,
                        len(good_ratios),
                        len(bad_ratios),
                        scope,
                    )
                )

        return patterns
