"""
Modality Ablation — measure true modality contribution by zeroing each input.

TRIBE was trained with 30% modality dropout, so it handles missing modalities
gracefully.  Run 4 forward passes: baseline + 3 with one modality zeroed.
Delta = true contribution of that modality.

Usage
-----
    from ablation import compute_modality_ablation

    contrib = compute_modality_ablation(
        baseline_predictions=preds,
        predictions_no_visual=preds_no_vis,
        predictions_no_audio=preds_no_aud,
        predictions_no_text=preds_no_txt,
    )
    print(contrib.to_dict())
    # {"visual_contribution": 52.3, "audio_contribution": 31.1, "text_contribution": 16.6, ...}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class ModalityContribution:
    """True modality contribution measured by ablation, not brain-region proxy.

    Fractions sum to 1.0 (within floating-point precision).
    """

    visual_contribution: float   # 0–1, fraction of total brain response from video
    audio_contribution: float    # 0–1, fraction from audio
    text_contribution: float     # 0–1, fraction from text

    visual_delta: np.ndarray     # (n_trs, 20484) — per-vertex delta when visual removed
    audio_delta: np.ndarray      # per-vertex delta when audio removed
    text_delta: np.ndarray       # per-vertex delta when text removed

    @property
    def dominant_modality(self) -> str:
        """Name of the modality that contributes most."""
        vals = {
            "visual": self.visual_contribution,
            "audio": self.audio_contribution,
            "text": self.text_contribution,
        }
        return max(vals, key=lambda k: vals[k])

    def to_dict(self) -> dict:
        """Serialisable summary (no large arrays)."""
        return {
            "visual_contribution": round(self.visual_contribution * 100, 1),
            "audio_contribution": round(self.audio_contribution * 100, 1),
            "text_contribution": round(self.text_contribution * 100, 1),
            "dominant_modality": self.dominant_modality,
            # Per-vertex mean absolute delta (one float per modality) for quick inspection
            "visual_delta_mean": round(float(self.visual_delta.mean()), 6),
            "audio_delta_mean": round(float(self.audio_delta.mean()), 6),
            "text_delta_mean": round(float(self.text_delta.mean()), 6),
        }

    def top_affected_vertices(self, modality: str = "visual", top_k: int = 100) -> np.ndarray:
        """Return vertex indices most changed when *modality* is removed.

        modality: "visual" | "audio" | "text"
        Returns shape (top_k,) sorted by descending mean delta.
        """
        delta_map = {
            "visual": self.visual_delta,
            "audio": self.audio_delta,
            "text": self.text_delta,
        }
        delta = delta_map.get(modality)
        if delta is None:
            raise ValueError(f"Unknown modality: {modality!r}")
        per_vertex = delta.mean(axis=0) if delta.ndim > 1 else delta
        return np.argsort(per_vertex)[::-1][:top_k]


def compute_modality_ablation(
    baseline_predictions: np.ndarray,
    predictions_no_visual: Optional[np.ndarray],
    predictions_no_audio: Optional[np.ndarray],
    predictions_no_text: Optional[np.ndarray],
) -> ModalityContribution:
    """Compute true modality contribution from ablation results.

    Parameters
    ----------
    baseline_predictions:
        Full model output, shape (n_trs, 20484).
    predictions_no_visual:
        Model output with the visual channel zeroed, same shape.
        Pass None if this ablation was not run (contribution treated as 0).
    predictions_no_audio:
        Model output with audio zeroed.
    predictions_no_text:
        Model output with text zeroed.

    Returns
    -------
    ModalityContribution with fractions and per-vertex delta arrays.

    Notes
    -----
    Contribution = mean |baseline - ablated| across all vertices and TRs,
    then normalised so that all three fractions sum to 1.  This mirrors
    how SHAP-style ablation attribution works: a large delta when a modality
    is removed means that modality was doing more work.
    """

    def _delta(ablated: Optional[np.ndarray]) -> np.ndarray:
        if ablated is None:
            return np.zeros_like(baseline_predictions)
        return np.abs(baseline_predictions - ablated)

    d_visual = _delta(predictions_no_visual)
    d_audio = _delta(predictions_no_audio)
    d_text = _delta(predictions_no_text)

    v_mean = float(d_visual.mean())
    a_mean = float(d_audio.mean())
    t_mean = float(d_text.mean())

    total = v_mean + a_mean + t_mean

    if total < 1e-8:
        # No meaningful signal — return equal split as fallback
        return ModalityContribution(
            visual_contribution=1 / 3,
            audio_contribution=1 / 3,
            text_contribution=1 / 3,
            visual_delta=d_visual,
            audio_delta=d_audio,
            text_delta=d_text,
        )

    return ModalityContribution(
        visual_contribution=v_mean / total,
        audio_contribution=a_mean / total,
        text_contribution=t_mean / total,
        visual_delta=d_visual,
        audio_delta=d_audio,
        text_delta=d_text,
    )


def run_ablation_suite(model, events_fn, content_path: str) -> ModalityContribution:
    """Convenience wrapper: run all 4 passes and return contributions.

    model: a loaded TribeModel (from tribev2.demo_utils)
    events_fn: callable(content_path, **kwargs) → events dataframe
    content_path: path to video/audio/text file

    The model must support `zero_modality` kwarg in predict() or equivalent
    mechanism.  Adapt this if TRIBE's API changes.
    """
    events = events_fn(content_path)

    baseline, _ = model.predict(events=events)

    try:
        events_no_vis = events_fn(content_path, zero_visual=True)
        preds_no_vis, _ = model.predict(events=events_no_vis)
    except Exception:
        preds_no_vis = None

    try:
        events_no_aud = events_fn(content_path, zero_audio=True)
        preds_no_aud, _ = model.predict(events=events_no_aud)
    except Exception:
        preds_no_aud = None

    try:
        events_no_txt = events_fn(content_path, zero_text=True)
        preds_no_txt, _ = model.predict(events=events_no_txt)
    except Exception:
        preds_no_txt = None

    return compute_modality_ablation(baseline, preds_no_vis, preds_no_aud, preds_no_txt)
