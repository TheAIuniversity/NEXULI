"""
RGB Brain Overlay — encode text / audio / video contributions as R/G/B on the
brain surface.

Pattern from TRIBE's own plotting code (cortical.py plot_surf_rgb).
Maps three modality-ablation delta signals to RGB channels so you see all
contributions simultaneously.

Channel mapping
---------------
    R (red)   = text contribution
    G (green) = audio contribution
    B (blue)  = video contribution

Colour interpretation
---------------------
    Pure red   → only text driving activation there
    Pure green → only audio
    Pure blue  → only video
    Yellow     → text + audio, no video
    Cyan       → audio + video, no text
    Magenta    → text + video, no audio
    White      → all three modalities contributing equally

Usage
-----
    from rgb_brain import compute_rgb_brain

    rgb_data = compute_rgb_brain(
        baseline=preds,
        no_text=preds_no_text,
        no_audio=preds_no_audio,
        no_video=preds_no_video,
    )
    # rgb_data.rgb_vertices  →  (20484, 3) float32, each channel 0-1
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


_N_VERTICES: int = 20484


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class RGBBrainData:
    """Per-vertex RGB values encoding modality contributions.

    rgb_vertices: (20484, 3) float32, values in [0, 1].
    Inactive vertices (total ablation delta below threshold) are set to a
    neutral grey (0.4, 0.4, 0.4).
    """

    rgb_vertices: np.ndarray      # (20484, 3) — R=text, G=audio, B=video

    # Dominance counts
    text_dominant_count: int       # vertices where text > audio and text > video
    audio_dominant_count: int
    video_dominant_count: int
    mixed_count: int               # no single modality clearly dominates
    below_threshold_count: int     # inactive vertices (rendered grey)

    def to_dict(self) -> dict:
        """Serialisable summary.  Does NOT include the full vertex array
        because at 20484 × 3 floats it is 500 KB+ JSON — pass rgb_vertices
        directly to the frontend via binary or a dedicated endpoint."""
        total_active = (
            self.text_dominant_count
            + self.audio_dominant_count
            + self.video_dominant_count
            + self.mixed_count
        )
        return {
            "text_dominant_pct": _pct(self.text_dominant_count),
            "audio_dominant_pct": _pct(self.audio_dominant_count),
            "video_dominant_pct": _pct(self.video_dominant_count),
            "mixed_pct": _pct(self.mixed_count),
            "below_threshold_pct": _pct(self.below_threshold_count),
            "active_vertex_count": total_active,
        }

    def to_json_safe(self) -> dict:
        """Full dict including vertex RGB data as nested list (for JSON responses).

        Large payload — use only for small surfaces or when absolutely needed.
        """
        d = self.to_dict()
        d["rgb_vertices"] = self.rgb_vertices.tolist()
        return d

    def dominant_region_mask(self, modality: str) -> np.ndarray:
        """Return boolean mask of vertices where *modality* is dominant.

        modality: "text" | "audio" | "video"
        """
        channel_map = {"text": 0, "audio": 1, "video": 2}
        if modality not in channel_map:
            raise ValueError(f"modality must be 'text', 'audio', or 'video', got {modality!r}")
        ch = channel_map[modality]
        r = self.rgb_vertices[:, ch]
        other = [self.rgb_vertices[:, i] for i in range(3) if i != ch]
        return (r > other[0]) & (r > other[1])


def _pct(count: int) -> float:
    return round(count / _N_VERTICES * 100, 1)


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def compute_rgb_brain(
    baseline: np.ndarray,
    no_text: np.ndarray,
    no_audio: np.ndarray,
    no_video: np.ndarray,
    threshold: float = 0.05,
    mixed_margin: float = 0.15,
) -> RGBBrainData:
    """Compute per-vertex RGB from modality ablation deltas.

    Parameters
    ----------
    baseline, no_text, no_audio, no_video:
        TRIBE predictions — shape (n_trs, 20484) or (20484,).
        If 2-D, the mean across TRs is taken first.
    threshold:
        Vertices whose total ablation delta falls below this value are
        considered inactive and rendered grey.
    mixed_margin:
        If the top channel exceeds the second-highest by less than this,
        the vertex is counted as "mixed" rather than assigned a dominant modality.

    Returns
    -------
    RGBBrainData with rgb_vertices (20484, 3) in [0, 1].
    """

    def _temporal_mean(arr: np.ndarray) -> np.ndarray:
        return arr.mean(axis=0) if arr.ndim > 1 else arr

    b = _temporal_mean(baseline)
    nt = _temporal_mean(no_text)
    na = _temporal_mean(no_audio)
    nv = _temporal_mean(no_video)

    # Per-vertex contribution delta for each modality
    text_contrib = np.abs(b - nt)    # → R channel
    audio_contrib = np.abs(b - na)   # → G channel
    video_contrib = np.abs(b - nv)   # → B channel

    # Stack to (20484, 3)
    rgb = np.stack([text_contrib, audio_contrib, video_contrib], axis=1).astype(np.float32)

    # Identify inactive vertices (total signal below threshold)
    total_signal = rgb.sum(axis=1)   # (20484,)
    inactive_mask = total_signal < threshold

    # Normalise active vertices: max channel → 1 per vertex
    max_vals = rgb.max(axis=1, keepdims=True)               # (20484, 1)
    max_vals = np.maximum(max_vals, 1e-8)
    rgb_norm = rgb / max_vals

    # Set inactive vertices to neutral grey
    rgb_norm[inactive_mask] = 0.4

    # Count dominance on active vertices only
    text_dom = 0
    audio_dom = 0
    video_dom = 0
    mixed = 0
    below = int(inactive_mask.sum())

    # Vectorised dominance counting on active subset
    active_rgb = rgb_norm[~inactive_mask]   # (n_active, 3)
    if len(active_rgb) > 0:
        # Sort each row descending to get top and second-highest channel
        sorted_vals = np.sort(active_rgb, axis=1)[:, ::-1]   # descending
        top_vals = sorted_vals[:, 0]
        second_vals = sorted_vals[:, 1]
        margin = top_vals - second_vals

        mixed_mask = margin < mixed_margin

        top_channel = active_rgb.argmax(axis=1)  # 0=text, 1=audio, 2=video

        mixed += int(mixed_mask.sum())
        text_dom += int((~mixed_mask & (top_channel == 0)).sum())
        audio_dom += int((~mixed_mask & (top_channel == 1)).sum())
        video_dom += int((~mixed_mask & (top_channel == 2)).sum())

    return RGBBrainData(
        rgb_vertices=rgb_norm,
        text_dominant_count=text_dom,
        audio_dominant_count=audio_dom,
        video_dominant_count=video_dom,
        mixed_count=mixed,
        below_threshold_count=below,
    )


# ---------------------------------------------------------------------------
# Time-resolved RGB (per-TR animation frames)
# ---------------------------------------------------------------------------

def compute_rgb_brain_timeseries(
    baseline: np.ndarray,
    no_text: np.ndarray,
    no_audio: np.ndarray,
    no_video: np.ndarray,
    threshold: float = 0.02,
) -> list[np.ndarray]:
    """Return one (20484, 3) RGB frame per TR for animation.

    baseline, no_*: all (n_trs, 20484).

    Returns: list of (20484, 3) float32 arrays, one per TR.
    """
    if baseline.ndim != 2:
        raise ValueError("Time-series mode requires 2-D input arrays (n_trs, 20484).")

    n_trs = baseline.shape[0]
    frames: list[np.ndarray] = []

    for i in range(n_trs):
        b_i = baseline[i]
        nt_i = no_text[i]
        na_i = no_audio[i]
        nv_i = no_video[i]

        rgb_data = compute_rgb_brain(
            baseline=b_i,
            no_text=nt_i,
            no_audio=na_i,
            no_video=nv_i,
            threshold=threshold,
        )
        frames.append(rgb_data.rgb_vertices)

    return frames
