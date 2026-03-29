"""
Temporal Dynamics — analyse cross-second patterns in TRIBE predictions.

The 8-layer transformer captures temporal dependencies up to the full
content window.  We extract: per-region gradients, cross-region attention
flow (lag-correlation), temporal coherence (autocorrelation), engagement
momentum, and critical transition moments.

Dependencies: numpy only.

Usage
-----
    from temporal import analyze_temporal_dynamics
    from atlas import get_vertex_atlas

    atlas = get_vertex_atlas()
    dynamics = analyze_temporal_dynamics(predictions, atlas)
    print(dynamics.to_dict())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np


# ---------------------------------------------------------------------------
# Temporal constant
# ---------------------------------------------------------------------------

TRIBE_TR: float = 0.5    # seconds per TR at TRIBE's native 2 Hz output


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class TemporalDynamics:
    """Cross-second analysis of brain activation patterns."""

    # Per-region temporal gradients (rising / falling / flat)
    gradients: dict
    # Format: {region_name: {"trend": "rising"|"falling"|"flat",
    #                        "slope": float, "volatility": float}}

    # Attention flow: does activation in region A predict activation in B later?
    attention_flows: List[dict]
    # Format: [{from_region, to_region, lag_trs, lag_seconds, correlation}]

    # Temporal coherence: smooth vs jerky activation patterns
    coherence_score: float   # 0-1 (1 = smooth flow, 0 = jerky re-engagement)

    # Engagement momentum: is overall activation accelerating or decelerating?
    momentum: float          # positive = building, negative = declining
    momentum_curve: List[float]  # per-TR momentum values

    # Critical transitions: TRs where the overall activation pattern shifts sharply
    transitions: List[dict]
    # Format: [{tr, second, from_level, to_level, magnitude, direction}]

    def to_dict(self) -> dict:
        return {
            "gradients": self.gradients,
            "attention_flows": self.attention_flows[:10],       # top 10
            "coherence_score": round(self.coherence_score, 3),
            "momentum": round(self.momentum, 3),
            "momentum_curve": [round(m, 3) for m in self.momentum_curve],
            "transitions": self.transitions,
            "n_regions_analysed": len(self.gradients),
            "n_attention_flows": len(self.attention_flows),
            "n_transitions": len(self.transitions),
        }

    def summary(self) -> str:
        """One-line human-readable summary."""
        trend_counts: dict[str, int] = {}
        for info in self.gradients.values():
            t = info["trend"]
            trend_counts[t] = trend_counts.get(t, 0) + 1

        dominant_trend = max(trend_counts, key=lambda k: trend_counts[k], default="flat")
        direction = "building" if self.momentum > 0.001 else ("declining" if self.momentum < -0.001 else "stable")
        return (
            f"Engagement is {direction} (momentum={self.momentum:+.3f}). "
            f"Most regions are {dominant_trend}. "
            f"Coherence: {self.coherence_score:.2f}. "
            f"{len(self.transitions)} critical transition(s)."
        )


# ---------------------------------------------------------------------------
# Analysis function
# ---------------------------------------------------------------------------

def analyze_temporal_dynamics(
    predictions: np.ndarray,
    region_indices: dict[str, np.ndarray],
    max_flow_lag_trs: int = 5,
    flow_corr_threshold: float = 0.3,
    transition_std_multiplier: float = 2.0,
) -> TemporalDynamics:
    """Full temporal analysis of TRIBE predictions.

    Parameters
    ----------
    predictions:
        Shape (n_trs, 20484) — raw TRIBE output at 2 Hz.
    region_indices:
        {region_name: vertex_indices} from atlas.get_vertex_atlas().
    max_flow_lag_trs:
        Maximum lag (in TRs) to check for cross-region attention flow.
    flow_corr_threshold:
        Minimum |correlation| to include an attention flow in results.
    transition_std_multiplier:
        A jump of this many stdev above the mean jump magnitude is a transition.

    Returns
    -------
    TemporalDynamics dataclass.
    """
    n_trs, n_verts = predictions.shape

    # ------------------------------------------------------------------
    # 1. Per-region time series
    # ------------------------------------------------------------------
    region_timeseries: dict[str, np.ndarray] = {}
    for name, indices in region_indices.items():
        if len(indices) == 0:
            continue
        valid = indices[indices < n_verts]
        if len(valid) == 0:
            continue
        region_timeseries[name] = predictions[:, valid].mean(axis=1)

    # ------------------------------------------------------------------
    # 2. Temporal gradients per region
    # ------------------------------------------------------------------
    gradients: dict[str, dict] = {}
    x = np.arange(n_trs, dtype=float)

    for name, ts in region_timeseries.items():
        if len(ts) < 3:
            continue

        # Linear slope via numpy polyfit
        slope = float(np.polyfit(x, ts, 1)[0])

        # Volatility: standard deviation of first differences
        diffs = np.diff(ts)
        volatility = float(np.std(diffs)) if len(diffs) > 0 else 0.0

        # Classify trend
        if abs(slope) < 1e-4:
            trend = "flat"
        elif slope > 0:
            trend = "rising"
        else:
            trend = "falling"

        gradients[name] = {
            "trend": trend,
            "slope": round(slope, 6),
            "volatility": round(volatility, 5),
        }

    # ------------------------------------------------------------------
    # 3. Attention flow: lagged cross-correlations between region pairs
    # ------------------------------------------------------------------
    attention_flows: list[dict] = []
    region_names = list(region_timeseries.keys())
    n_regions = len(region_names)

    for i in range(n_regions):
        for j in range(i + 1, n_regions):
            name_a = region_names[i]
            name_b = region_names[j]
            ts_a = region_timeseries[name_a]
            ts_b = region_timeseries[name_b]

            best_lag = 0
            best_corr = 0.0

            for lag in range(1, min(max_flow_lag_trs + 1, n_trs // 2)):
                if lag >= len(ts_a):
                    break
                try:
                    corr = float(np.corrcoef(ts_a[:-lag], ts_b[lag:])[0, 1])
                except Exception:
                    continue
                if np.isnan(corr):
                    continue
                if abs(corr) > abs(best_corr):
                    best_corr = corr
                    best_lag = lag

            if abs(best_corr) >= flow_corr_threshold:
                attention_flows.append({
                    "from_region": name_a,
                    "to_region": name_b,
                    "lag_trs": best_lag,
                    "lag_seconds": round(best_lag * TRIBE_TR, 1),
                    "correlation": round(best_corr, 3),
                })

    # Sort by absolute correlation (strongest flows first)
    attention_flows.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    # ------------------------------------------------------------------
    # 4. Temporal coherence — lag-1 autocorrelation of the global signal
    # ------------------------------------------------------------------
    overall = predictions.mean(axis=1)   # (n_trs,) — global average per TR

    if n_trs > 2:
        try:
            autocorr = float(np.corrcoef(overall[:-1], overall[1:])[0, 1])
            coherence = float(np.clip(autocorr, 0.0, 1.0)) if not np.isnan(autocorr) else 0.5
        except Exception:
            coherence = 0.5
    else:
        coherence = 0.5

    # ------------------------------------------------------------------
    # 5. Engagement momentum — gradient of the global signal
    # ------------------------------------------------------------------
    if n_trs > 2:
        momentum_arr = np.gradient(overall)
        momentum_curve = [float(m) for m in momentum_arr]
        momentum = float(np.mean(momentum_arr))
    else:
        momentum_curve = [0.0] * n_trs
        momentum = 0.0

    # ------------------------------------------------------------------
    # 6. Critical transitions — spikes / drops beyond 2σ
    # ------------------------------------------------------------------
    transitions: list[dict] = []
    if n_trs > 3:
        abs_diffs = np.abs(np.diff(overall))
        threshold = (
            float(np.mean(abs_diffs))
            + transition_std_multiplier * float(np.std(abs_diffs))
        )
        for idx, d in enumerate(abs_diffs):
            if float(d) > threshold:
                from_level = float(overall[idx])
                to_level = float(overall[idx + 1])
                transitions.append({
                    "tr": idx + 1,
                    "second": round((idx + 1) * TRIBE_TR, 1),
                    "from_level": round(from_level, 5),
                    "to_level": round(to_level, 5),
                    "magnitude": round(float(d), 5),
                    "direction": "spike" if to_level > from_level else "drop",
                })

    return TemporalDynamics(
        gradients=gradients,
        attention_flows=attention_flows,
        coherence_score=coherence,
        momentum=momentum,
        momentum_curve=momentum_curve,
        transitions=transitions,
    )


# ---------------------------------------------------------------------------
# Convenience: sliding-window engagement curve
# ---------------------------------------------------------------------------

def sliding_engagement(
    predictions: np.ndarray,
    window_trs: int = 4,
) -> np.ndarray:
    """Compute a smoothed engagement curve using a rolling mean.

    predictions: (n_trs, 20484)
    window_trs:  rolling window size in TRs (default = 4 TRs = 2 seconds at 2 Hz)

    Returns: (n_trs,) smoothed mean absolute activation per TR.
    """
    overall = np.abs(predictions).mean(axis=1)
    if window_trs <= 1:
        return overall

    kernel = np.ones(window_trs) / window_trs
    smoothed = np.convolve(overall, kernel, mode="same")

    # Fix edge effects: first and last half-window use a narrower average
    half = window_trs // 2
    for i in range(half):
        w = i + 1
        smoothed[i] = overall[:w].mean()
        smoothed[-(i + 1)] = overall[-(w):].mean()

    return smoothed
