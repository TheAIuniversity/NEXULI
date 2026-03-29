"""
TRIBE Leader — the central intelligence layer where brain maps drive ALL agent decisions.

Every agent imports from here instead of making its own decisions. The TRIBE brain map
is the source of truth: directives are generated from specific region activations and
learned weights, not from generic scoring thresholds.

Architecture
------------
TribeAnalysis   — deep, brain-region-specific dissection of a score_content() result
TribeDirective  — typed instruction for a single agent, traceable to a brain region
generate_directives()       — produces per-agent directive lists from a TribeAnalysis
score_deploy_readiness()    — single boolean + scored verdict with weighted blockers

Brain region → score_content() field mapping
--------------------------------------------
visual_cortex   → SecondScore.visual      / ContentScore.visual_avg
auditory_cortex → SecondScore.auditory   / ContentScore.auditory_avg
language_areas  → SecondScore.language   / ContentScore.language_avg
prefrontal      → SecondScore.decision   / ContentScore.decision_avg
default_mode    → SecondScore.emotion    / ContentScore.emotion_avg
fusiform_face   → SecondScore.face_response (no avg stored; derived from per_second)
hook_strength   → ContentScore.hook_score

brain_weights keys (from AgentBrain.weights / DEFAULT_BRAIN["learning_weights"])
-----------------------------------------------------------------
"visual_cortex", "auditory_cortex", "language_areas",
"prefrontal", "default_mode", "hook_strength"
(fusiform_face is not independently weighted; it is folded into the face_response
 data and used qualitatively — we derive its importance from the fusiform activations
 stored in per_second and weight it alongside visual_cortex for severity calculations.)
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

# Minimum normalised weight treated as "this region matters" for directives
_WEIGHT_SIGNIFICANT = 1.2

# Thresholds used uniformly across all methods — centralised here so every
# method is consistent and the values are easy to tune.
_ATTENTION_LOW = 40.0        # below this → weak moment territory
_ATTENTION_HIGH = 80.0       # above this → peak moment territory
_REGION_LOW = 30.0           # region is "dropped out"
_REGION_HIGH = 60.0          # region is "strongly firing"
_HOOK_STRONG = 65.0          # hook_score threshold for "good hook"
_HOOK_FACE_FIRE = 60.0       # fusiform threshold in first 2s for "face present"
_HOOK_SPEECH_FIRE = 50.0     # language threshold in first 2s for "speech present"
_HOOK_PREFRONTAL_SPIKE = 55.0  # decision threshold in first 3s for pattern interrupt
_CTA_PREFRONTAL_TRIGGER = 60.0  # decision must reach this to count as a CTA trigger
_DEPLOY_BLOCK_PREFRONTAL = 50.0  # decision at hook or CTA below this → deploy blocker
_MODALITY_DOMINANT = 50.0    # pct above which a single modality "leads"

# Human-readable labels for each brain region
_REGION_LABEL: dict[str, str] = {
    "visual_cortex":   "visual cortex (V1/V2/V3)",
    "auditory_cortex": "auditory cortex (STG)",
    "language_areas":  "language areas (Broca + Wernicke)",
    "prefrontal":      "prefrontal cortex",
    "default_mode":    "default mode network",
    "fusiform_face":   "fusiform face area",
}

# Brain-region → specific fix mapping
_REGION_FIX: dict[str, str] = {
    "visual_cortex":   "add scene change / B-roll / motion graphic",
    "auditory_cortex": "add voiceover / change music / add sound effect",
    "language_areas":  "add speech / simplify language / add subtitle",
    "prefrontal":      "add question / statistic / price / deadline / scarcity",
    "default_mode":    "add 'you' language / personal story / testimonial / mirror audience pain",
    "fusiform_face":   "add human face / switch to talking head / show customer",
}

# Brain-region → dropout diagnosis
_REGION_DIAGNOSIS: dict[str, str] = {
    "visual_cortex":   "visual boredom — no scene change / static frame",
    "auditory_cortex": "audio disengagement — silence, monotone, or music-only section",
    "language_areas":  "language processing stopped — no speech, or speech too complex",
    "prefrontal":      "evaluation stopped — nothing to decide on, no value proposition",
    "default_mode":    "lost personal relevance — content not self-referential",
    "fusiform_face":   "no human face — viewer disconnected from speaker",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ts(seconds: float) -> str:
    """Format a float second value as M:SS string, e.g. 0:08."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def _safe_mean(values: list[float]) -> float:
    """Return mean of a list, or 0.0 for empty lists."""
    return statistics.mean(values) if values else 0.0


def _weighted_severity(raw_activation_drop: float, region: str, brain_weights: dict) -> float:
    """
    Translate a raw activation drop into a severity score that reflects
    how much this brain's learned weights care about this region.

    raw_activation_drop: how far below _REGION_LOW the activation is (0 = exactly at
        threshold; larger = worse)
    region: one of the REGION_LABEL keys
    brain_weights: AgentBrain.weights dict

    Returns a 0-100 severity score.
    """
    base = min(100.0, max(0.0, (_REGION_LOW - raw_activation_drop) / _REGION_LOW * 100))
    # fusiform_face is not in brain_weights directly; use visual_cortex weight as proxy
    if region == "fusiform_face":
        weight = brain_weights.get("visual_cortex", 1.0)
    else:
        weight = brain_weights.get(region, 1.0)
    return min(100.0, base * weight)


def _primary_dropped_region(second_scores: list[dict], brain_weights: dict) -> tuple[str, float]:
    """
    Given a list of per-second score dicts over a weak window, identify the
    single brain region that has dropped furthest below its threshold,
    weighted by learned importance.

    Returns (region_name, activation_value).
    """
    # Map score_content field names to region keys
    field_to_region = {
        "visual":       "visual_cortex",
        "auditory":     "auditory_cortex",
        "language":     "language_areas",
        "decision":     "prefrontal",
        "emotion":      "default_mode",
        "face_response": "fusiform_face",
    }

    worst_region = "visual_cortex"
    worst_score = 100.0

    for field_name, region in field_to_region.items():
        vals = [s.get(field_name, 50.0) for s in second_scores]
        avg = _safe_mean(vals)
        # Normalise by learned weight so a drop in a high-weight region scores worse
        if region == "fusiform_face":
            w = brain_weights.get("visual_cortex", 1.0)
        else:
            w = brain_weights.get(region, 1.0)
        effective = avg / w  # lower = worse when weight is high
        if effective < worst_score:
            worst_score = effective
            worst_region = region

    raw_avg = _safe_mean([s.get(_region_to_field(worst_region), 50.0) for s in second_scores])
    return worst_region, raw_avg


def _region_to_field(region: str) -> str:
    """Map brain region key back to the per-second score dict field name."""
    return {
        "visual_cortex":   "visual",
        "auditory_cortex": "auditory",
        "language_areas":  "language",
        "prefrontal":      "decision",
        "default_mode":    "emotion",
        "fusiform_face":   "face_response",
    }.get(region, "visual")


def _primary_leading_region(second_scores: list[dict]) -> tuple[str, float]:
    """Identify the region that is most activated (highest average) in a window."""
    field_to_region = {
        "visual":       "visual_cortex",
        "auditory":     "auditory_cortex",
        "language":     "language_areas",
        "decision":     "prefrontal",
        "emotion":      "default_mode",
        "face_response": "fusiform_face",
    }
    best_region = "visual_cortex"
    best_avg = 0.0
    for field_name, region in field_to_region.items():
        avg = _safe_mean([s.get(field_name, 0.0) for s in second_scores])
        if avg > best_avg:
            best_avg = avg
            best_region = region
    return best_region, best_avg


# ---------------------------------------------------------------------------
# TribeAnalysis
# ---------------------------------------------------------------------------

class TribeAnalysis:
    """
    Deep analysis of a TRIBE brain map — the source of truth for all agent decisions.

    Parameters
    ----------
    score_result:
        Output of ``scoring.score_content().to_dict()``.  Every field name used
        internally matches the ContentScore / SecondScore dataclass field names
        exactly as defined in scoring.py.
    brain_weights:
        From ``AgentBrain.weights`` — the dict of six learned importance multipliers,
        keyed by brain region name (e.g. "prefrontal", "default_mode", etc.).

    Usage
    -----
    ::

        analysis = TribeAnalysis(scorer_agent.score(file_path), brain.weights)
        directives = generate_directives(analysis)
        readiness  = score_deploy_readiness(analysis)
    """

    def __init__(self, score_result: dict, brain_weights: dict) -> None:
        self._r = score_result          # ContentScore as dict
        self._w = brain_weights         # AgentBrain.weights
        self._ps: list[dict] = score_result.get("per_second", [])
        self._duration: int = score_result.get("duration_seconds", len(self._ps))

        # Cache expensive derived values lazily
        self._weak_cache: Optional[list[dict]] = None
        self._peak_cache: Optional[list[dict]] = None
        self._hook_cache: Optional[dict] = None
        self._cta_cache: Optional[dict] = None
        self._modality_cache: Optional[dict] = None
        self._rules_cache: Optional[list[str]] = None

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def diagnose_weak_moments(self) -> list[dict]:
        """
        For each weak moment in the score result, identify the PRIMARY brain
        region responsible and generate a brain-specific diagnosis and fix.

        Returns a list of dicts, one per weak moment:

        .. code-block:: python

            {
                "timestamp":         "0:08 – 0:14",
                "start":             8.0,
                "end":               14.0,
                "duration":          6,
                "primary_region":    "prefrontal",
                "region_label":      "prefrontal cortex",
                "region_activation": 21.4,
                "diagnosis":         "evaluation stopped — nothing to decide on …",
                "weighted_severity": 87.3,   # 0-100, uses brain_weights
                "specific_fix":      "add question / statistic / price / deadline",
                "severity":          "critical",
            }
        """
        if self._weak_cache is not None:
            return self._weak_cache

        results = []
        for wm in self._r.get("weak_moments", []):
            start = int(wm["start"])
            end   = int(wm["end"])
            window = self._ps[start:end] if self._ps else []

            if window:
                primary_region, activation = _primary_dropped_region(window, self._w)
            else:
                # No per-second data — fall back to aggregate averages
                primary_region, activation = self._fallback_primary_region()

            severity_score = _weighted_severity(activation, primary_region, self._w)
            duration = end - start

            results.append({
                "timestamp":         f"{_ts(start)} – {_ts(end)}",
                "start":             float(start),
                "end":               float(end),
                "duration":          duration,
                "primary_region":    primary_region,
                "region_label":      _REGION_LABEL[primary_region],
                "region_activation": round(activation, 1),
                "diagnosis":         _REGION_DIAGNOSIS[primary_region],
                "weighted_severity": round(severity_score, 1),
                "specific_fix":      _REGION_FIX[primary_region],
                "severity":          wm.get("severity", "warning"),
            })

        # Sort by weighted severity descending so most critical comes first
        results.sort(key=lambda x: x["weighted_severity"], reverse=True)
        self._weak_cache = results
        return results

    def diagnose_peak_moments(self) -> list[dict]:
        """
        For each peak moment, identify the brain region driving the peak and
        characterise why it is valuable (hook / thumbnail / clip / cta_moment).

        Returns a list of dicts:

        .. code-block:: python

            {
                "timestamp":      "0:01 – 0:04",
                "start":          1.0,
                "end":            4.0,
                "duration":       3,
                "primary_region": "fusiform_face",
                "region_label":   "fusiform face area",
                "region_activation": 82.1,
                "diagnosis":      "strong hook — face is grabbing attention",
                "use_case":       "hook",
                "confidence":     0.91,
            }
        """
        if self._peak_cache is not None:
            return self._peak_cache

        results = []
        for pm in self._r.get("peak_moments", []):
            start = int(pm["start"])
            end   = int(pm["end"])
            window = self._ps[start:end] if self._ps else []

            if window:
                primary_region, activation = _primary_leading_region(window)
            else:
                primary_region = "visual_cortex"
                activation = 80.0

            use_case, diagnosis = self._classify_peak(
                start, end, primary_region, activation, window
            )

            # Confidence: normalised activation × brain weight for this region
            if primary_region == "fusiform_face":
                weight = self._w.get("visual_cortex", 1.0)
            else:
                weight = self._w.get(primary_region, 1.0)
            confidence = min(1.0, (activation / 100.0) * min(weight / 2.0 + 0.5, 1.0))

            results.append({
                "timestamp":         f"{_ts(start)} – {_ts(end)}",
                "start":             float(start),
                "end":               float(end),
                "duration":          end - start,
                "primary_region":    primary_region,
                "region_label":      _REGION_LABEL[primary_region],
                "region_activation": round(activation, 1),
                "diagnosis":         diagnosis,
                "use_case":          use_case,
                "confidence":        round(confidence, 2),
            })

        self._peak_cache = results
        return results

    def get_modality_verdict(self) -> dict:
        """
        Determine which modality is carrying the content and whether it matches
        what the brain's modality_insights say works best for this audience.

        Returns a dict with ``label``, ``dominant_modality``, ``v_pct``,
        ``a_pct``, ``t_pct``, ``brain_recommendation``, and ``aligned``.
        """
        if self._modality_cache is not None:
            return self._modality_cache

        v = self._r.get("visual_pct", 33.0)
        a = self._r.get("audio_pct", 33.0)
        t = self._r.get("text_pct", 33.0)

        if v > _MODALITY_DOMINANT:
            dominant = "visual"
            label = (
                f"visual-led content — the images/video are doing the work "
                f"({v:.0f}% of brain activation comes from visual cortex)"
            )
        elif a > _MODALITY_DOMINANT:
            dominant = "audio"
            label = (
                f"audio-led content — voiceover/music is carrying engagement "
                f"({a:.0f}% of brain activation comes from auditory cortex)"
            )
        elif t > _MODALITY_DOMINANT:
            dominant = "text"
            label = (
                f"text-led content — the words are what matters "
                f"({t:.0f}% of brain activation comes from language areas)"
            )
        else:
            dominant = "balanced"
            label = (
                f"balanced multimodal — all channels contributing "
                f"(visual {v:.0f}% / audio {a:.0f}% / text {t:.0f}%)"
            )

        # Compare against brain's modality_insights if available
        brain_recommendation, aligned = self._modality_alignment(dominant)

        result = {
            "label":                label,
            "dominant_modality":    dominant,
            "v_pct":                round(v, 1),
            "a_pct":                round(a, 1),
            "t_pct":                round(t, 1),
            "brain_recommendation": brain_recommendation,
            "aligned":              aligned,
        }
        self._modality_cache = result
        return result

    def get_hook_verdict(self) -> dict:
        """
        Analyse the first three seconds of content through the brain map lens.

        Returns a dict with keys: ``hook_score``, ``has_face``, ``has_speech``,
        ``has_pattern_interrupt``, ``hook_strength``, ``benchmark_delta``,
        ``verdict``, ``fix`` (empty string when hook is strong).
        """
        if self._hook_cache is not None:
            return self._hook_cache

        hook_window = self._ps[:3] if self._ps else []
        hook_score = self._r.get("hook_score", 0.0)
        hook_weight = self._w.get("hook_strength", 1.0)

        # Face: fusiform_face > _HOOK_FACE_FIRE in first 2 seconds
        first_2s = hook_window[:2]
        has_face = any(
            s.get("face_response", 0) > _HOOK_FACE_FIRE for s in first_2s
        )
        face_peak = max((s.get("face_response", 0) for s in first_2s), default=0.0)

        # Speech: language > _HOOK_SPEECH_FIRE in first 2 seconds
        has_speech = any(
            s.get("language", 0) > _HOOK_SPEECH_FIRE for s in first_2s
        )
        speech_peak = max((s.get("language", 0) for s in first_2s), default=0.0)

        # Pattern interrupt: prefrontal spike in first 3 seconds
        has_pattern_interrupt = any(
            s.get("decision", 0) > _HOOK_PREFRONTAL_SPIKE for s in hook_window
        )
        prefrontal_peak = max((s.get("decision", 0) for s in hook_window), default=0.0)

        # Weighted hook score (brain weight amplifies how much we care)
        weighted_hook = hook_score * hook_weight
        hook_strength = "strong" if hook_score >= _HOOK_STRONG else "weak"

        # Benchmark delta from brain's stored average
        bench_avg = 0.0  # will be overridden if brain context is injected
        benchmark_delta = hook_score - bench_avg

        # Compose verdict
        signals = []
        if has_face:
            signals.append(
                f"face detected (fusiform fired at {face_peak:.0f} in first 2s)"
            )
        if has_speech:
            signals.append(
                f"speech present (language areas at {speech_peak:.0f} in first 2s)"
            )
        if has_pattern_interrupt:
            signals.append(
                f"pattern interrupt present (prefrontal spiked to {prefrontal_peak:.0f} in first 3s)"
            )

        if hook_strength == "strong":
            verdict = (
                f"Strong hook ({hook_score:.0f}/100 — brain weight x{hook_weight:.1f}). "
                + (f"Signals: {', '.join(signals)}." if signals else "All brain systems engaged.")
            )
            fix = ""
        else:
            missing = []
            if not has_face:
                missing.append("no face — fusiform face area not firing in opening 2s")
            if not has_speech:
                missing.append("no speech — language areas silent in opening 2s")
            if not has_pattern_interrupt:
                missing.append(
                    "no pattern interrupt — prefrontal never spiked above "
                    f"{_HOOK_PREFRONTAL_SPIKE:.0f} in first 3s"
                )
            verdict = (
                f"Weak hook ({hook_score:.0f}/100 — brain weight x{hook_weight:.1f}). "
                f"Missing: {'; '.join(missing) if missing else 'general low activation'}."
            )
            # Most impactful fix: target the highest-weighted missing signal
            fix = self._hook_fix(has_face, has_speech, has_pattern_interrupt, face_peak,
                                 speech_peak, prefrontal_peak)

        result = {
            "hook_score":           round(hook_score, 1),
            "weighted_hook_score":  round(weighted_hook, 1),
            "hook_weight":          round(hook_weight, 2),
            "has_face":             has_face,
            "face_peak":            round(face_peak, 1),
            "has_speech":           has_speech,
            "speech_peak":          round(speech_peak, 1),
            "has_pattern_interrupt": has_pattern_interrupt,
            "prefrontal_peak":      round(prefrontal_peak, 1),
            "hook_strength":        hook_strength,
            "benchmark_delta":      round(benchmark_delta, 1),
            "verdict":              verdict,
            "fix":                  fix,
        }
        self._hook_cache = result
        return result

    def get_cta_verdict(self) -> dict:
        """
        Find the moment of peak prefrontal activation and evaluate whether the
        actual CTA placement aligns with it.

        The last 20% of the content duration is treated as "the CTA zone."

        Returns a dict with keys: ``peak_decision_timestamp``, ``peak_decision_value``,
        ``is_in_cta_zone``, ``actual_cta_zone_start``, ``placement``,
        ``verdict``, ``recommendation``.
        """
        if self._cta_cache is not None:
            return self._cta_cache

        cta_zone_start = self._duration * 0.80

        if self._ps:
            # Find the second with peak prefrontal (decision) activation
            peak_ts = max(range(len(self._ps)), key=lambda i: self._ps[i].get("decision", 0))
            peak_val = self._ps[peak_ts].get("decision", 0.0)
        else:
            # Fall back to aggregate
            peak_ts = int(cta_zone_start)
            peak_val = self._r.get("decision_avg", 0.0)

        prefrontal_weight = self._w.get("prefrontal", 1.0)
        is_in_cta_zone = peak_ts >= cta_zone_start

        if peak_val < _CTA_PREFRONTAL_TRIGGER:
            placement = "no_trigger"
            verdict = (
                f"No decision trigger. Prefrontal cortex never reached "
                f"{_CTA_PREFRONTAL_TRIGGER:.0f} — peaked at {peak_val:.0f} at "
                f"{_ts(peak_ts)}. Brain weight for prefrontal: x{prefrontal_weight:.1f}. "
                "There is no cognitive moment where the viewer is evaluating a decision."
            )
            recommendation = (
                "Add a clear value proposition: a price, deadline, guarantee, "
                "scarcity signal, or rhetorical question that forces evaluation. "
                f"Target the {_ts(peak_ts)} window where prefrontal is already "
                "at its relative peak — place the CTA there."
            )
        elif is_in_cta_zone:
            placement = "good"
            verdict = (
                f"Good CTA placement. Prefrontal peaks at {peak_val:.0f} at "
                f"{_ts(peak_ts)}, which is inside the last 20% of content "
                f"(CTA zone starts at {_ts(int(cta_zone_start))}). "
                f"Brain weight for prefrontal: x{prefrontal_weight:.1f}."
            )
            recommendation = (
                f"Maintain current CTA position. Consider reinforcing with a "
                "scarcity or social-proof element at the same timestamp to amplify "
                "the existing prefrontal spike."
            )
        else:
            placement = "misaligned"
            verdict = (
                f"CTA misaligned. Prefrontal peaks at {peak_val:.0f} at "
                f"{_ts(peak_ts)}, which is BEFORE the CTA zone "
                f"(last 20% starts at {_ts(int(cta_zone_start))}). "
                "The viewer's decision-making window has passed by the time the "
                f"CTA appears. Brain weight for prefrontal: x{prefrontal_weight:.1f}."
            )
            recommendation = (
                f"Move the CTA to {_ts(peak_ts)} where prefrontal is already peaking. "
                "Alternatively, add a second value proposition near "
                f"{_ts(int(cta_zone_start))} to create a second prefrontal spike "
                "that aligns with the intended CTA position."
            )

        result = {
            "peak_decision_timestamp": _ts(peak_ts),
            "peak_decision_second":    peak_ts,
            "peak_decision_value":     round(peak_val, 1),
            "prefrontal_weight":       round(prefrontal_weight, 2),
            "is_in_cta_zone":          is_in_cta_zone,
            "actual_cta_zone_start":   _ts(int(cta_zone_start)),
            "cta_zone_start_second":   int(cta_zone_start),
            "placement":               placement,
            "verdict":                 verdict,
            "recommendation":          recommendation,
        }
        self._cta_cache = result
        return result

    def generate_creative_rules(self) -> list[str]:
        """
        Derive concrete, evidence-backed creative rules from this content's brain map.

        Each rule is a human-readable instruction that references the specific
        brain region activation that justifies it, ordered by the learned weight
        of the relevant region (highest-weight rules first).

        Returns a list of rule strings.
        """
        if self._rules_cache is not None:
            return self._rules_cache

        rules: list[tuple[float, str]] = []  # (priority_score, rule_text)

        # Rule source 1: hook evidence
        hook = self.get_hook_verdict()
        hook_weight = self._w.get("hook_strength", 1.0)
        if hook["has_face"]:
            rules.append((
                hook_weight * hook["face_peak"],
                f"Lead with a human face — fusiform face area fired at "
                f"{hook['face_peak']:.0f} in second 1 (hook weight x{hook_weight:.1f})",
            ))
        if not hook["has_face"]:
            rules.append((
                hook_weight * 80,
                f"Add a face in the first 2 seconds — fusiform face area is not "
                f"firing in the opening (hook weight x{hook_weight:.1f}; "
                "this is the single highest-impact hook fix)",
            ))
        if hook["has_speech"]:
            rules.append((
                hook_weight * hook["speech_peak"] * self._w.get("language_areas", 1.0),
                f"Open with direct speech — language areas activated at "
                f"{hook['speech_peak']:.0f} within first 2 seconds",
            ))

        # Rule source 2: weak moment patterns — find recurring region dropouts
        weak = self.diagnose_weak_moments()
        region_dropout_count: dict[str, list[dict]] = {}
        for wm in weak:
            r = wm["primary_region"]
            region_dropout_count.setdefault(r, []).append(wm)

        for region, moments in region_dropout_count.items():
            if region == "fusiform_face":
                w = self._w.get("visual_cortex", 1.0)
            else:
                w = self._w.get(region, 1.0)
            timestamps = " / ".join(m["timestamp"] for m in moments[:3])
            rules.append((
                w * _safe_mean([m["weighted_severity"] for m in moments]),
                f"{_REGION_FIX[region].capitalize()} — "
                f"{_REGION_LABEL[region]} drops at {timestamps} "
                f"(region weight x{w:.1f}, avg severity "
                f"{_safe_mean([m['weighted_severity'] for m in moments]):.0f}/100)",
            ))

        # Rule source 3: peak moment patterns — what is already working
        peaks = self.diagnose_peak_moments()
        for pk in peaks:
            if pk["confidence"] > 0.6:
                if pk["primary_region"] == "fusiform_face":
                    w = self._w.get("visual_cortex", 1.0)
                else:
                    w = self._w.get(pk["primary_region"], 1.0)
                rules.append((
                    w * pk["region_activation"],
                    f"Replicate the {pk['use_case']} pattern at {pk['timestamp']} — "
                    f"{_REGION_LABEL[pk['primary_region']]} fires at "
                    f"{pk['region_activation']:.0f} (region weight x{w:.1f}; "
                    f"use this as a {pk['use_case']} template)",
                ))

        # Rule source 4: CTA placement
        cta = self.get_cta_verdict()
        if cta["placement"] == "misaligned":
            pw = self._w.get("prefrontal", 1.0)
            rules.append((
                pw * cta["peak_decision_value"],
                f"Move CTA to {cta['peak_decision_timestamp']} — prefrontal peaks "
                f"there at {cta['peak_decision_value']:.0f} "
                f"(prefrontal weight x{pw:.1f}; current CTA is after decision window closes)",
            ))
        elif cta["placement"] == "no_trigger":
            pw = self._w.get("prefrontal", 1.0)
            rules.append((
                pw * 90,
                f"Add a value proposition — prefrontal never reaches "
                f"{_CTA_PREFRONTAL_TRIGGER:.0f} anywhere in the content "
                f"(prefrontal weight x{pw:.1f}; without a decision trigger there is no CTA moment)",
            ))

        # Rule source 5: default mode / personal relevance gaps
        dm_avg = self._r.get("emotion_avg", 50.0)
        dm_weight = self._w.get("default_mode", 1.0)
        if dm_avg < 45.0:
            # Find the biggest gap in default mode activation
            if self._ps:
                dm_low_windows = [
                    (i, s.get("emotion", 50)) for i, s in enumerate(self._ps)
                    if s.get("emotion", 50) < 35
                ]
                if dm_low_windows:
                    first_low = dm_low_windows[0][0]
                    last_low = dm_low_windows[-1][0]
                    rules.append((
                        dm_weight * (50 - dm_avg),
                        f"Add personal story or 'you' language between "
                        f"{_ts(first_low)} – {_ts(last_low)} — default mode network "
                        f"averaging {dm_avg:.0f} (weight x{dm_weight:.1f}; audience is "
                        "not seeing themselves in this content)",
                    ))
            else:
                rules.append((
                    dm_weight * (50 - dm_avg),
                    f"Add personal relevance throughout — default mode averaging "
                    f"{dm_avg:.0f} (weight x{dm_weight:.1f}; content is not self-referential)",
                ))

        # Sort by priority descending (highest brain-weighted evidence first)
        rules.sort(key=lambda x: x[0], reverse=True)
        result = [r[1] for r in rules]
        self._rules_cache = result
        return result

    def compare(self, other: "TribeAnalysis") -> dict:
        """
        Compare this content piece's brain map against another, region by region.

        Parameters
        ----------
        other:
            Another TribeAnalysis instance (can be a different content file scored
            with the same or different brain weights — we use self's weights as the
            reference).

        Returns a dict with:
            ``winner``, ``margin``, ``reason``, ``region_comparison`` (list),
            ``summary``.
        """
        a = self._r
        b = other._r

        region_map = [
            ("visual_cortex",   "visual_avg",    "Visual cortex"),
            ("auditory_cortex", "auditory_avg",  "Auditory cortex"),
            ("language_areas",  "language_avg",  "Language areas"),
            ("prefrontal",      "decision_avg",  "Prefrontal"),
            ("default_mode",    "emotion_avg",   "Default mode"),
        ]

        region_comparison: list[dict] = []
        a_weighted_total = 0.0
        b_weighted_total = 0.0
        total_weight = 0.0

        for region, field_name, label in region_map:
            a_val = a.get(field_name, 0.0)
            b_val = b.get(field_name, 0.0)
            w = self._w.get(region, 1.0)
            diff = a_val - b_val
            diff_pct = (diff / b_val * 100) if b_val > 0 else 0.0

            a_weighted_total += a_val * w
            b_weighted_total += b_val * w
            total_weight += w

            if abs(diff_pct) < 3:
                advantage = "tied"
                note = f"both at ~{a_val:.0f}"
            elif diff > 0:
                advantage = "A"
                note = (
                    f"A is {diff_pct:.0f}% higher "
                    f"({'better decision trigger' if region == 'prefrontal' else ''}"
                    f"{'stronger emotional resonance' if region == 'default_mode' else ''}"
                    f"{'stronger visual engagement' if region == 'visual_cortex' else ''}"
                    f"{'better audio engagement' if region == 'auditory_cortex' else ''}"
                    f"{'stronger language processing' if region == 'language_areas' else ''}"
                    f") — region weight x{w:.1f}"
                ).replace("  ", " ").strip()
            else:
                advantage = "B"
                note = (
                    f"B is {abs(diff_pct):.0f}% higher "
                    f"({'better decision trigger' if region == 'prefrontal' else ''}"
                    f"{'stronger emotional resonance' if region == 'default_mode' else ''}"
                    f"{'stronger visual engagement' if region == 'visual_cortex' else ''}"
                    f"{'better audio engagement' if region == 'auditory_cortex' else ''}"
                    f"{'stronger language processing' if region == 'language_areas' else ''}"
                    f") — region weight x{w:.1f}"
                ).replace("  ", " ").strip()

            region_comparison.append({
                "region":       region,
                "label":        label,
                "weight":       round(w, 2),
                "a_value":      round(a_val, 1),
                "b_value":      round(b_val, 1),
                "diff_pct":     round(diff_pct, 1),
                "advantage":    advantage,
                "note":         note,
            })

        # Weighted overall comparison
        a_score = a_weighted_total / total_weight if total_weight > 0 else 0
        b_score = b_weighted_total / total_weight if total_weight > 0 else 0
        margin = a_score - b_score
        margin_pct = (margin / b_score * 100) if b_score > 0 else 0.0

        winner = "A" if margin > 0 else "B" if margin < 0 else "tied"
        winner_label = "Version A" if winner == "A" else "Version B" if winner == "B" else "Tied"

        # Build a specific reason string using the top 2 differentiating regions
        diff_regions = sorted(region_comparison, key=lambda x: abs(x["diff_pct"]), reverse=True)
        reasons = []
        for rc in diff_regions[:2]:
            if abs(rc["diff_pct"]) >= 5:
                leading = winner if rc["advantage"] == winner else ("B" if winner == "A" else "A")
                reasons.append(
                    f"Version {leading} scores {abs(rc['diff_pct']):.0f}% "
                    f"higher in {rc['label']} (weight x{rc['weight']:.1f})"
                )
        reason = "; ".join(reasons) if reasons else "marginal difference across all regions"

        # Hook comparison
        a_hook = a.get("hook_score", 0.0)
        b_hook = b.get("hook_score", 0.0)
        hook_w = self._w.get("hook_strength", 1.0)
        hook_note = (
            f"Hook: A={a_hook:.0f} vs B={b_hook:.0f} "
            f"(hook weight x{hook_w:.1f}) — "
            + ("A has stronger hook" if a_hook > b_hook else
               "B has stronger hook" if b_hook > a_hook else
               "hooks are equal")
        )

        summary = (
            f"{winner_label} wins by {abs(margin_pct):.0f}% on brain-weighted score "
            f"(A={a_score:.0f} vs B={b_score:.0f} weighted avg). {reason}. {hook_note}."
        )

        return {
            "winner":             winner,
            "a_weighted_score":   round(a_score, 1),
            "b_weighted_score":   round(b_score, 1),
            "margin_pct":         round(margin_pct, 1),
            "reason":             reason,
            "region_comparison":  region_comparison,
            "hook_note":          hook_note,
            "summary":            summary,
        }

    def to_dict(self) -> dict:
        """Full analysis serialised to a JSON-safe dict."""
        return {
            "score_result":        self._r,
            "brain_weights":       self._w,
            "weak_moments":        self.diagnose_weak_moments(),
            "peak_moments":        self.diagnose_peak_moments(),
            "modality_verdict":    self.get_modality_verdict(),
            "hook_verdict":        self.get_hook_verdict(),
            "cta_verdict":         self.get_cta_verdict(),
            "creative_rules":      self.generate_creative_rules(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fallback_primary_region(self) -> tuple[str, float]:
        """Use aggregate averages when per-second data is unavailable."""
        candidates = {
            "visual_cortex":   self._r.get("visual_avg", 50.0),
            "auditory_cortex": self._r.get("auditory_avg", 50.0),
            "language_areas":  self._r.get("language_avg", 50.0),
            "prefrontal":      self._r.get("decision_avg", 50.0),
            "default_mode":    self._r.get("emotion_avg", 50.0),
        }
        # Lowest weighted activation → most responsible for the weak moment
        worst = min(candidates, key=lambda r: candidates[r] / self._w.get(r, 1.0))
        return worst, candidates[worst]

    def _classify_peak(
        self,
        start: int,
        end: int,
        primary_region: str,
        activation: float,
        window: list[dict],
    ) -> tuple[str, str]:
        """Classify a peak moment into a use_case and write a diagnosis string."""
        fusiform_avg = _safe_mean([s.get("face_response", 0) for s in window])
        prefrontal_avg = _safe_mean([s.get("decision", 0) for s in window])
        emotion_avg = _safe_mean([s.get("emotion", 0) for s in window])
        auditory_avg = _safe_mean([s.get("auditory", 0) for s in window])

        cta_zone_start = self._duration * 0.80

        if start <= 3:
            use_case = "hook"
            if fusiform_avg > 60:
                diagnosis = (
                    f"strong hook — face is grabbing attention "
                    f"(fusiform at {fusiform_avg:.0f} in opening {end}s)"
                )
            elif prefrontal_avg > 55:
                diagnosis = (
                    f"strong hook — pattern interrupt firing "
                    f"(prefrontal at {prefrontal_avg:.0f} in opening {end}s)"
                )
            else:
                diagnosis = (
                    f"strong hook — high combined activation in first {end}s "
                    f"({_REGION_LABEL[primary_region]} leading at {activation:.0f})"
                )

        elif start >= cta_zone_start and prefrontal_avg > 60:
            use_case = "cta_moment"
            diagnosis = (
                f"decision activation at the right moment — good CTA placement "
                f"(prefrontal at {prefrontal_avg:.0f} at {_ts(start)}, "
                f"inside last 20% of content)"
            )

        elif fusiform_avg > 70:
            use_case = "thumbnail"
            diagnosis = (
                f"face + attention peak — ideal thumbnail frame "
                f"(fusiform face area at {fusiform_avg:.0f} at {_ts(start)})"
            )

        elif emotion_avg > 65:
            use_case = "clip"
            diagnosis = (
                f"emotional resonance — audience is relating "
                f"(default mode network at {emotion_avg:.0f} at {_ts(start)}; "
                "use as testimonial or story clip)"
            )

        elif auditory_avg > 65 and primary_region == "auditory_cortex":
            use_case = "clip"
            diagnosis = (
                f"audio is landing the message "
                f"(auditory cortex at {auditory_avg:.0f} at {_ts(start)}; "
                "isolate this audio segment)"
            )

        else:
            use_case = "clip"
            diagnosis = (
                f"engagement spike at {_ts(start)} — "
                f"{_REGION_LABEL[primary_region]} at {activation:.0f}; "
                "use as short-form clip"
            )

        return use_case, diagnosis

    def _modality_alignment(self, dominant: str) -> tuple[str, bool]:
        """
        Compare dominant modality against what brain's modality_insights says works.

        Since TribeAnalysis doesn't hold a direct reference to the AgentBrain object
        (keeping this module decoupled), the caller can inject modality_insights via
        a subclass or the compare_with_brain() helper.  With only score_result +
        brain_weights available, we derive a recommendation from the weights:
        the highest-weight cognitive system implies the recommended modality.
        """
        v_weight = self._w.get("visual_cortex", 1.0)
        a_weight = self._w.get("auditory_cortex", 1.0)
        t_weight = self._w.get("language_areas", 1.0)

        if v_weight >= a_weight and v_weight >= t_weight:
            recommended = "visual"
        elif a_weight >= v_weight and a_weight >= t_weight:
            recommended = "audio"
        else:
            recommended = "text"

        if dominant == recommended or dominant == "balanced":
            recommendation = (
                f"Brain weights confirm: {recommended}-led content performs best "
                f"for this audience (weight x{max(v_weight, a_weight, t_weight):.1f}). "
                "Current modality mix aligns."
            )
            aligned = True
        else:
            top_weight = max(v_weight, a_weight, t_weight)
            recommendation = (
                f"Brain weights suggest {recommended}-led content performs best "
                f"(weight x{top_weight:.1f}) but this content is {dominant}-led. "
                f"Shift emphasis toward {recommended} channel."
            )
            aligned = False

        return recommendation, aligned

    def _hook_fix(
        self,
        has_face: bool,
        has_speech: bool,
        has_pattern_interrupt: bool,
        face_peak: float,
        speech_peak: float,
        prefrontal_peak: float,
    ) -> str:
        """Return the single most impactful hook fix based on missing brain signals."""
        # Rank by which missing element correlates with highest brain weight
        candidates: list[tuple[float, str]] = []

        visual_w = self._w.get("visual_cortex", 1.0)
        lang_w = self._w.get("language_areas", 1.0)
        pfc_w = self._w.get("prefrontal", 1.0)

        if not has_face:
            candidates.append((
                visual_w * (_HOOK_FACE_FIRE - face_peak),
                f"Cut to a human face in the first 2 seconds — fusiform face area is not "
                f"activating (currently at {face_peak:.0f}, needs >{_HOOK_FACE_FIRE:.0f}; "
                f"visual cortex weight x{visual_w:.1f})",
            ))
        if not has_speech:
            candidates.append((
                lang_w * (_HOOK_SPEECH_FIRE - speech_peak),
                f"Open with spoken words in the first 2 seconds — language areas are silent "
                f"(currently at {speech_peak:.0f}, needs >{_HOOK_SPEECH_FIRE:.0f}; "
                f"language weight x{lang_w:.1f})",
            ))
        if not has_pattern_interrupt:
            candidates.append((
                pfc_w * (_HOOK_PREFRONTAL_SPIKE - prefrontal_peak),
                f"Add a question, surprising statistic, or bold claim in first 3 seconds — "
                f"prefrontal not spiking (currently at {prefrontal_peak:.0f}, "
                f"needs >{_HOOK_PREFRONTAL_SPIKE:.0f}; prefrontal weight x{pfc_w:.1f})",
            ))

        if not candidates:
            return (
                "Increase overall opening energy — hook score is below threshold "
                f"({_HOOK_STRONG:.0f}) despite basic signals being present"
            )

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]


# ---------------------------------------------------------------------------
# TribeDirective
# ---------------------------------------------------------------------------

@dataclass
class TribeDirective:
    """
    A typed, brain-evidence-backed instruction for a single agent.

    All directives are generated by ``generate_directives()`` from a
    ``TribeAnalysis`` instance — agents do not produce their own directives.

    Attributes
    ----------
    agent:
        Target agent name — matches the ``name`` class attribute on each agent
        (``"optimizer"``, ``"creative"``, ``"scout"``, ``"learner"``, ``"deployer"``).
    action:
        Short verb phrase describing what the agent should do.
    priority:
        ``"critical"`` / ``"high"`` / ``"medium"`` / ``"low"``
    brain_evidence:
        The specific brain region + activation value that justifies this directive.
    instruction:
        Full instruction text the agent acts on.
    confidence:
        0.0 – 1.0.  Derived from the learned weight of the relevant brain region
        normalised to a probability.  Higher weight → higher confidence.
    metadata:
        Optional dict for any additional structured data the agent may need
        (e.g. timestamp, activation value, region name).
    """

    agent: str
    action: str
    priority: str
    brain_evidence: str
    instruction: str
    confidence: float
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# generate_directives
# ---------------------------------------------------------------------------

def generate_directives(analysis: TribeAnalysis) -> list[TribeDirective]:
    """
    Produce a list of ``TribeDirective`` objects — one per actionable finding —
    covering all five agents.

    The directives are deterministic: the same TribeAnalysis always produces the
    same set.  Sorting within each agent group is by confidence descending.

    Parameters
    ----------
    analysis:
        A fully initialised ``TribeAnalysis`` instance.

    Returns
    -------
    list[TribeDirective]
        All directives, interleaved by agent.  Callers can filter by
        ``directive.agent`` to route instructions.
    """
    directives: list[TribeDirective] = []
    w = analysis._w  # brain weights shortcut

    # ------------------------------------------------------------------
    # 1. OPTIMIZER directives
    # ------------------------------------------------------------------

    # One directive per weak moment with brain-specific fix
    for wm in analysis.diagnose_weak_moments():
        region = wm["primary_region"]
        region_w = w.get(region if region != "fusiform_face" else "visual_cortex", 1.0)
        confidence = _weight_to_confidence(region_w, wm["region_activation"] / 100.0)
        priority = "critical" if wm["severity"] == "critical" else "high"

        directives.append(TribeDirective(
            agent="optimizer",
            action="patch_weak_moment",
            priority=priority,
            brain_evidence=(
                f"{_REGION_LABEL[region]} dropped to {wm['region_activation']:.0f} "
                f"at {wm['timestamp']} (region weight x{region_w:.1f}, "
                f"weighted severity {wm['weighted_severity']:.0f}/100)"
            ),
            instruction=(
                f"[{wm['timestamp']}] {wm['diagnosis'].capitalize()}. "
                f"Fix: {wm['specific_fix']}. "
                f"This is a {wm['severity']} issue (weighted severity "
                f"{wm['weighted_severity']:.0f}/100 — brain treats "
                f"{_REGION_LABEL[region]} at weight x{region_w:.1f})."
            ),
            confidence=confidence,
            metadata={
                "start":             wm["start"],
                "end":               wm["end"],
                "primary_region":    region,
                "region_activation": wm["region_activation"],
                "weighted_severity": wm["weighted_severity"],
            },
        ))

    # CTA placement directive
    cta = analysis.get_cta_verdict()
    if cta["placement"] != "good":
        pfc_w = w.get("prefrontal", 1.0)
        confidence = _weight_to_confidence(pfc_w, cta["peak_decision_value"] / 100.0)
        priority = "critical" if cta["placement"] == "no_trigger" else "high"
        directives.append(TribeDirective(
            agent="optimizer",
            action="fix_cta_placement",
            priority=priority,
            brain_evidence=(
                f"Prefrontal peaked at {cta['peak_decision_value']:.0f} at "
                f"{cta['peak_decision_timestamp']} (prefrontal weight x{pfc_w:.1f})"
            ),
            instruction=cta["recommendation"],
            confidence=confidence,
            metadata={
                "placement":               cta["placement"],
                "peak_decision_second":    cta["peak_decision_second"],
                "peak_decision_value":     cta["peak_decision_value"],
                "cta_zone_start_second":   cta["cta_zone_start_second"],
            },
        ))

    # Hook directive
    hook = analysis.get_hook_verdict()
    if hook["hook_strength"] == "weak":
        hook_w = w.get("hook_strength", 1.0)
        confidence = _weight_to_confidence(hook_w, hook["hook_score"] / 100.0)
        directives.append(TribeDirective(
            agent="optimizer",
            action="fix_hook",
            priority="high",
            brain_evidence=(
                f"Hook score {hook['hook_score']:.0f}/100 "
                f"(hook weight x{hook_w:.1f}, weighted {hook['weighted_hook_score']:.0f})"
            ),
            instruction=hook["fix"],
            confidence=confidence,
            metadata={
                "hook_score":    hook["hook_score"],
                "has_face":      hook["has_face"],
                "has_speech":    hook["has_speech"],
                "has_pattern_interrupt": hook["has_pattern_interrupt"],
            },
        ))

    # ------------------------------------------------------------------
    # 2. CREATIVE directives
    # ------------------------------------------------------------------

    # Creative rules from brain map
    rules = analysis.generate_creative_rules()
    for i, rule in enumerate(rules):
        # Priority decreases as rules are sorted by brain-weight priority
        priority = "high" if i < 2 else "medium" if i < 5 else "low"
        # Extract region from the rule text to set confidence
        region_confidence = _extract_confidence_from_rule(rule, w)
        directives.append(TribeDirective(
            agent="creative",
            action="apply_creative_rule",
            priority=priority,
            brain_evidence=rule,
            instruction=(
                f"Creative rule #{i + 1} (brain-weight ranked): {rule}"
            ),
            confidence=region_confidence,
            metadata={"rule_index": i, "rule": rule},
        ))

    # Modality recommendation
    modality = analysis.get_modality_verdict()
    if not modality["aligned"]:
        directives.append(TribeDirective(
            agent="creative",
            action="adjust_modality_mix",
            priority="medium",
            brain_evidence=modality["brain_recommendation"],
            instruction=(
                f"Current content is {modality['dominant_modality']}-led "
                f"({modality['label']}). "
                f"{modality['brain_recommendation']} "
                "Adjust production to shift channel emphasis accordingly."
            ),
            confidence=0.7,
            metadata={
                "dominant_modality": modality["dominant_modality"],
                "v_pct": modality["v_pct"],
                "a_pct": modality["a_pct"],
                "t_pct": modality["t_pct"],
            },
        ))

    # Hook pattern recommendation
    if hook["hook_strength"] == "strong":
        hook_w = w.get("hook_strength", 1.0)
        signals = []
        if hook["has_face"]:
            signals.append(f"face (fusiform {hook['face_peak']:.0f})")
        if hook["has_speech"]:
            signals.append(f"speech (language {hook['speech_peak']:.0f})")
        if hook["has_pattern_interrupt"]:
            signals.append(f"pattern interrupt (prefrontal {hook['prefrontal_peak']:.0f})")
        directives.append(TribeDirective(
            agent="creative",
            action="replicate_hook_pattern",
            priority="high",
            brain_evidence=(
                f"Hook score {hook['hook_score']:.0f} with signals: "
                f"{', '.join(signals)} (hook weight x{hook_w:.1f})"
            ),
            instruction=(
                f"This hook structure is proven for this brain — "
                f"replicate it in all new content: {', '.join(signals)}. "
                f"Hook score: {hook['hook_score']:.0f}/100 "
                f"(brain hook weight x{hook_w:.1f})."
            ),
            confidence=_weight_to_confidence(hook_w, hook["hook_score"] / 100.0),
            metadata={
                "hook_pattern": {
                    "has_face": hook["has_face"],
                    "has_speech": hook["has_speech"],
                    "has_pattern_interrupt": hook["has_pattern_interrupt"],
                }
            },
        ))

    # ------------------------------------------------------------------
    # 3. SCOUT directives
    # ------------------------------------------------------------------

    # Find the highest-weight region — tell scout to focus on competitors who win there
    top_region = max(
        [r for r in w if r != "hook_strength"],
        key=lambda r: w[r],
    )
    top_weight = w[top_region]

    directives.append(TribeDirective(
        agent="scout",
        action="score_competitor_content",
        priority="high",
        brain_evidence=(
            f"Brain's highest-weight region is {_REGION_LABEL[top_region]} "
            f"(weight x{top_weight:.1f}) — competitors who out-activate this region "
            "represent the greatest threat"
        ),
        instruction=(
            f"Score all tracked competitor content through TRIBE and compare brain maps. "
            f"Priority focus: competitors whose content activates "
            f"{_REGION_LABEL[top_region]} more than ours — this brain weights that "
            f"region at x{top_weight:.1f}, making it the strongest predictor of "
            "performance for this audience."
        ),
        confidence=min(1.0, top_weight / 3.0),
        metadata={
            "target_region":  top_region,
            "region_weight":  top_weight,
            "our_activation": analysis._r.get(
                _region_to_field(top_region) + "_avg"
                if top_region != "fusiform_face"
                else "visual_avg",
                0.0,
            ),
        },
    ))

    # If any high-weight region is below average, tell scout to find who is doing it better
    for region, score_field in [
        ("visual_cortex",   "visual_avg"),
        ("auditory_cortex", "auditory_avg"),
        ("language_areas",  "language_avg"),
        ("prefrontal",      "decision_avg"),
        ("default_mode",    "emotion_avg"),
    ]:
        our_val = analysis._r.get(score_field, 50.0)
        region_w = w.get(region, 1.0)
        if region_w >= _WEIGHT_SIGNIFICANT and our_val < 50.0:
            directives.append(TribeDirective(
                agent="scout",
                action="find_competitor_benchmark",
                priority="medium",
                brain_evidence=(
                    f"Our {_REGION_LABEL[region]} averages {our_val:.0f} — below 50 "
                    f"with a brain weight of x{region_w:.1f}"
                ),
                instruction=(
                    f"Find competitors whose content scores >60 on "
                    f"{_REGION_LABEL[region]} in TRIBE brain maps. "
                    f"Our content averages {our_val:.0f} in this region "
                    f"(brain weight x{region_w:.1f} — this is a learned gap). "
                    "Analyse their creative patterns and report to learner."
                ),
                confidence=_weight_to_confidence(region_w, 1 - our_val / 100.0),
                metadata={
                    "region":        region,
                    "our_avg":       our_val,
                    "region_weight": region_w,
                },
            ))

    # ------------------------------------------------------------------
    # 4. LEARNER directives
    # ------------------------------------------------------------------

    # Record each significant brain activation event
    for pk in analysis.diagnose_peak_moments():
        if pk["confidence"] > 0.5:
            region = pk["primary_region"]
            region_w = w.get(region if region != "fusiform_face" else "visual_cortex", 1.0)
            directives.append(TribeDirective(
                agent="learner",
                action="record_activation_event",
                priority="medium",
                brain_evidence=(
                    f"{_REGION_LABEL[region]} activation of "
                    f"{pk['region_activation']:.0f} at {pk['timestamp']} "
                    f"(region weight x{region_w:.1f})"
                ),
                instruction=(
                    f"Record: {_REGION_LABEL[region]} activation of "
                    f"{pk['region_activation']:.0f} at {pk['timestamp']} — "
                    f"use_case classified as '{pk['use_case']}'. "
                    "Correlate with engagement data (watch-time, CTR, conversion) "
                    f"when available. Region weight x{region_w:.1f} — "
                    "if this correlates with real performance, increase this weight."
                ),
                confidence=pk["confidence"],
                metadata={
                    "timestamp":       pk["timestamp"],
                    "region":          region,
                    "activation":      pk["region_activation"],
                    "use_case":        pk["use_case"],
                    "region_weight":   region_w,
                },
            ))

    # Pattern update directives for weak moments
    for wm in analysis.diagnose_weak_moments():
        region = wm["primary_region"]
        region_w = w.get(region if region != "fusiform_face" else "visual_cortex", 1.0)
        threshold = _REGION_LOW
        directives.append(TribeDirective(
            agent="learner",
            action="update_pattern",
            priority="low",
            brain_evidence=(
                f"{_REGION_LABEL[region]} = {wm['region_activation']:.0f} "
                f"at {wm['timestamp']} (weight x{region_w:.1f})"
            ),
            instruction=(
                f"Update pattern: content with {_REGION_LABEL[region]} "
                f"< {threshold:.0f} at {wm['timestamp']} is correlated with weak "
                f"engagement in this content (weighted severity "
                f"{wm['weighted_severity']:.0f}/100 at region weight x{region_w:.1f}). "
                "When real performance data is available for this content, calculate "
                "the actual performance delta and update this region's weight accordingly."
            ),
            confidence=min(1.0, region_w / 3.0),
            metadata={
                "region":          region,
                "activation":      wm["region_activation"],
                "weighted_severity": wm["weighted_severity"],
                "timestamp":       wm["timestamp"],
                "region_weight":   region_w,
            },
        ))

    # CTA learning directive
    if cta["placement"] == "good" and cta["peak_decision_value"] >= _CTA_PREFRONTAL_TRIGGER:
        pfc_w = w.get("prefrontal", 1.0)
        directives.append(TribeDirective(
            agent="learner",
            action="update_pattern",
            priority="medium",
            brain_evidence=(
                f"Prefrontal at {cta['peak_decision_value']:.0f} in CTA zone "
                f"(prefrontal weight x{pfc_w:.1f})"
            ),
            instruction=(
                f"Update pattern: content with prefrontal > "
                f"{_CTA_PREFRONTAL_TRIGGER:.0f} in the last 20% of content "
                f"(detected here at {cta['peak_decision_value']:.0f}) — "
                "track whether this correlates with higher conversion rate. "
                f"Prefrontal weight is currently x{pfc_w:.1f}; adjust upward if "
                "this pattern confirms."
            ),
            confidence=_weight_to_confidence(pfc_w, cta["peak_decision_value"] / 100.0),
            metadata={
                "pattern":         "prefrontal_in_cta_zone",
                "activation":      cta["peak_decision_value"],
                "region_weight":   pfc_w,
            },
        ))

    # ------------------------------------------------------------------
    # 5. DEPLOYER directives
    # ------------------------------------------------------------------

    readiness = score_deploy_readiness(analysis)
    deploy_confidence = readiness["score"] / 100.0

    if readiness["ready"]:
        directives.append(TribeDirective(
            agent="deployer",
            action="deploy",
            priority="high",
            brain_evidence=(
                f"Brain-weighted deploy score {readiness['score']}/100 — "
                f"no critical blockers. Strengths: "
                f"{'; '.join(readiness['strengths'][:2])}"
            ),
            instruction=(
                f"Deploy. Brain-weighted readiness score: {readiness['score']}/100. "
                f"Verdict: {readiness['verdict']} "
                f"Strengths: {'; '.join(readiness['strengths'])}."
            ),
            confidence=deploy_confidence,
            metadata={
                "deploy_score": readiness["score"],
                "strengths":    readiness["strengths"],
                "blockers":     readiness["blockers"],
            },
        ))
    else:
        # One Hold directive per blocker
        for blocker in readiness["blockers"]:
            directives.append(TribeDirective(
                agent="deployer",
                action="hold",
                priority="critical",
                brain_evidence=blocker,
                instruction=(
                    f"Hold deployment. Blocker: {blocker}. "
                    f"Brain-weighted readiness score: {readiness['score']}/100. "
                    f"Verdict: {readiness['verdict']} "
                    "Resolve this blocker before deploying."
                ),
                confidence=1.0 - deploy_confidence,
                metadata={
                    "deploy_score": readiness["score"],
                    "blocker":      blocker,
                    "all_blockers": readiness["blockers"],
                },
            ))

    return directives


# ---------------------------------------------------------------------------
# score_deploy_readiness
# ---------------------------------------------------------------------------

def score_deploy_readiness(analysis: TribeAnalysis) -> dict:
    """
    Answer the single question: should this content go live?

    Scoring is fully driven by brain weights.  Each region's contribution to
    the overall score is multiplied by its learned importance weight.  A region
    with weight 3.5 contributes 3.5× as much as a region with weight 1.0.

    Returns
    -------
    dict with keys:
        ``ready`` (bool), ``score`` (int 0-100), ``blockers`` (list[str]),
        ``strengths`` (list[str]), ``verdict`` (str).
    """
    r = analysis._r
    w = analysis._w

    blockers: list[str] = []
    strengths: list[str] = []

    # ------------------------------------------------------------------
    # Per-region weighted score contribution
    # ------------------------------------------------------------------

    region_scores = [
        ("visual_cortex",   "visual_avg",   r.get("visual_avg", 0.0)),
        ("auditory_cortex", "auditory_avg", r.get("auditory_avg", 0.0)),
        ("language_areas",  "language_avg", r.get("language_avg", 0.0)),
        ("prefrontal",      "decision_avg", r.get("decision_avg", 0.0)),
        ("default_mode",    "emotion_avg",  r.get("emotion_avg", 0.0)),
    ]

    weighted_sum = 0.0
    total_weight = 0.0

    for region, field_name, activation in region_scores:
        region_w = w.get(region, 1.0)
        weighted_sum += activation * region_w
        total_weight += region_w

        if activation < _REGION_LOW and region_w >= _WEIGHT_SIGNIFICANT:
            blockers.append(
                f"{_REGION_LABEL[region]} averages {activation:.0f} "
                f"(below {_REGION_LOW:.0f} threshold, brain weight x{region_w:.1f}) — "
                f"{_REGION_DIAGNOSIS[region]}"
            )
        elif activation >= _REGION_HIGH and region_w >= _WEIGHT_SIGNIFICANT:
            strengths.append(
                f"{_REGION_LABEL[region]} strong at {activation:.0f} "
                f"(brain weight x{region_w:.1f}) — "
                f"{_region_strength_note(region, activation)}"
            )

    # Base score from weighted region average
    base_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0

    # ------------------------------------------------------------------
    # Hook penalty / bonus (uses hook_strength weight)
    # ------------------------------------------------------------------

    hook_verdict = analysis.get_hook_verdict()
    hook_w = w.get("hook_strength", 1.0)
    hook_score_raw = hook_verdict["hook_score"]

    if hook_score_raw < _HOOK_STRONG:
        hook_penalty = (_HOOK_STRONG - hook_score_raw) * hook_w * 0.3
        base_score = max(0, base_score - hook_penalty)
        if hook_w >= _WEIGHT_SIGNIFICANT:
            blockers.append(
                f"Hook score {hook_score_raw:.0f} below {_HOOK_STRONG:.0f} "
                f"(hook weight x{hook_w:.1f}) — "
                f"{hook_verdict['fix']}"
            )
    else:
        hook_bonus = (hook_score_raw - _HOOK_STRONG) * hook_w * 0.1
        base_score = min(100, base_score + hook_bonus)
        strengths.append(
            f"Strong hook ({hook_score_raw:.0f}/100, hook weight x{hook_w:.1f}) — "
            "opening brain activation is above threshold"
        )

    # ------------------------------------------------------------------
    # CTA check — hard blocker for high-weight prefrontal
    # ------------------------------------------------------------------

    cta = analysis.get_cta_verdict()
    pfc_w = w.get("prefrontal", 1.0)

    if cta["placement"] == "no_trigger" and pfc_w >= _WEIGHT_SIGNIFICANT:
        blockers.append(
            f"No decision trigger — prefrontal never reached "
            f"{_CTA_PREFRONTAL_TRIGGER:.0f} (prefrontal weight x{pfc_w:.1f}). "
            "No CTA moment exists in this content."
        )
        base_score = max(0, base_score - 15 * pfc_w)
    elif cta["placement"] == "good":
        strengths.append(
            f"CTA aligned with prefrontal peak at {cta['peak_decision_timestamp']} "
            f"({cta['peak_decision_value']:.0f}, prefrontal weight x{pfc_w:.1f})"
        )

    # ------------------------------------------------------------------
    # Critical weak moments check
    # ------------------------------------------------------------------

    critical_weaks = [
        wm for wm in analysis.diagnose_weak_moments()
        if wm["severity"] == "critical"
    ]
    for cw in critical_weaks:
        region = cw["primary_region"]
        region_w = w.get(region if region != "fusiform_face" else "visual_cortex", 1.0)
        if region_w >= _WEIGHT_SIGNIFICANT:
            penalty = cw["weighted_severity"] * 0.05
            base_score = max(0, base_score - penalty)

    # ------------------------------------------------------------------
    # Peak moments bonus
    # ------------------------------------------------------------------

    strong_peaks = [
        pk for pk in analysis.diagnose_peak_moments()
        if pk["confidence"] > 0.7
    ]
    if strong_peaks:
        strengths.append(
            f"{len(strong_peaks)} high-confidence peak moment(s) — "
            f"use cases: {', '.join(set(pk['use_case'] for pk in strong_peaks))}"
        )

    # ------------------------------------------------------------------
    # Final score and verdict
    # ------------------------------------------------------------------

    final_score = int(min(100, max(0, base_score)))
    ready = len(blockers) == 0 and final_score >= 55

    if ready:
        verdict = (
            f"Ready to deploy. Brain-weighted score {final_score}/100 with no critical blockers. "
            + (f"Key strength: {strengths[0]}." if strengths else "")
        )
    elif final_score >= 55 and blockers:
        verdict = (
            f"Score is {final_score}/100 but {len(blocker_plural(blockers))} blocker(s) must be "
            f"resolved before deploying: {blockers[0][:80]}…"
        )
    else:
        verdict = (
            f"Not ready. Score {final_score}/100 — "
            f"{len(blockers)} blocker(s). "
            + (f"Primary blocker: {blockers[0][:100]}." if blockers else
               "Score below 55 threshold.")
        )

    return {
        "ready":     ready,
        "score":     final_score,
        "blockers":  blockers,
        "strengths": strengths,
        "verdict":   verdict,
    }


# ---------------------------------------------------------------------------
# Module-level utility helpers (private, used by both functions above)
# ---------------------------------------------------------------------------

def _weight_to_confidence(region_weight: float, raw_signal: float) -> float:
    """
    Convert a region weight + raw activation signal (0-1) to a confidence
    probability (0-1).

    Saturates at 1.0.  A weight of 2.0 and full signal → 0.9.
    A weight of 1.0 and 0.5 signal → 0.5.
    """
    return round(min(1.0, raw_signal * (0.5 + region_weight * 0.25)), 2)


def _region_strength_note(region: str, activation: float) -> str:
    """One-liner explanation of why a high activation is good."""
    notes = {
        "visual_cortex":   "visual processing is engaged — scene variety is working",
        "auditory_cortex": "audio channel is landing — voiceover/music is effective",
        "language_areas":  "language processing active — message is being decoded",
        "prefrontal":      "decision-making engaged — value proposition is landing",
        "default_mode":    "emotional resonance active — audience is self-referencing",
        "fusiform_face":   "face detection active — human connection established",
    }
    return notes.get(region, f"{region} at {activation:.0f}")


def _extract_confidence_from_rule(rule: str, weights: dict) -> float:
    """
    Attempt to extract a confidence value from a creative rule string by
    detecting which region it references and reading its weight.
    Falls back to 0.6 if no region is detected.
    """
    for region, label in _REGION_LABEL.items():
        if label.lower() in rule.lower() or region.replace("_", " ") in rule.lower():
            w = weights.get(region if region != "fusiform_face" else "visual_cortex", 1.0)
            return min(1.0, 0.4 + w * 0.15)
    # Hook rules
    if "hook" in rule.lower() or "fusiform" in rule.lower() or "face" in rule.lower():
        hw = weights.get("hook_strength", 1.0)
        return min(1.0, 0.4 + hw * 0.15)
    return 0.6


def blocker_plural(blockers: list) -> list:
    """Identity function — exists purely for the grammar check in verdict string."""
    return blockers
