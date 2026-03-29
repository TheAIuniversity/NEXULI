"""
Segment Event Mapper — connects specific words, scenes, and audio moments to
their brain responses.

TRIBE returns segment objects that contain the events (words, audio, video)
that were playing at each prediction timestep.  This module maps
content → brain, giving you:
- Which words triggered the highest brain response
- Which timesteps had the highest / lowest activation
- Per-TR breakdown of what was happening in the content

Dependencies: numpy only.

Usage
-----
    from segment_mapper import map_segments_to_brain
    from atlas import get_vertex_atlas

    atlas = get_vertex_atlas()
    brain_map = map_segments_to_brain(predictions, segments, region_indices=atlas)
    print(brain_map.to_dict())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Temporal constant
# ---------------------------------------------------------------------------

TRIBE_TR: float = 0.5    # seconds per TR at 2 Hz


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ContentMoment:
    """A specific moment in the content with its brain response."""

    tr_index: int
    timestamp_seconds: float

    # What was happening in the content at this moment
    words: List[str] = field(default_factory=list)
    has_speech: bool = False
    has_video: bool = False
    has_audio: bool = False

    # Brain response at this moment
    overall_activation: float = 0.0
    top_regions: List[dict] = field(default_factory=list)   # [{name, activation}]

    def to_dict(self) -> dict:
        return {
            "tr": self.tr_index,
            "timestamp": round(self.timestamp_seconds, 1),
            "words": self.words,
            "has_speech": self.has_speech,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "overall_activation": round(self.overall_activation, 4),
            "top_regions": self.top_regions,
        }


@dataclass
class ContentBrainMap:
    """Full mapping of content moments to brain responses."""

    moments: List[ContentMoment]
    word_activations: dict       # {word: avg_activation} — which words are most impactful
    peak_moments: List[ContentMoment]     # top 5 by overall_activation
    weak_moments: List[ContentMoment]     # bottom 5 by overall_activation

    def to_dict(self) -> dict:
        return {
            "total_moments": len(self.moments),
            "duration_seconds": round(len(self.moments) * TRIBE_TR, 1),
            "word_activations": {
                w: round(a, 4)
                for w, a in sorted(
                    self.word_activations.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:20]
            },
            "peak_moments": [m.to_dict() for m in self.peak_moments],
            "weak_moments": [m.to_dict() for m in self.weak_moments],
        }

    def word_impact_ranking(self, top_k: int = 10) -> List[tuple[str, float]]:
        """Return (word, avg_activation) sorted by descending impact."""
        return sorted(self.word_activations.items(), key=lambda x: x[1], reverse=True)[:top_k]


# ---------------------------------------------------------------------------
# Event extraction helpers
# ---------------------------------------------------------------------------

def _safe_iter_events(seg) -> list:
    """Try several known TRIBE segment event formats and return event rows."""
    rows: list = []

    # Format A: seg.ns_events is a pandas DataFrame
    if hasattr(seg, "ns_events") and seg.ns_events is not None:
        events = seg.ns_events
        if hasattr(events, "iterrows"):
            try:
                for _, row in events.iterrows():
                    rows.append(row)
            except Exception:
                pass
        return rows

    # Format B: seg.events is a list of dicts / namedtuples
    if hasattr(seg, "events") and seg.events is not None:
        try:
            for ev in seg.events:
                rows.append(ev)
        except Exception:
            pass

    return rows


def _extract_event_info(event) -> tuple[Optional[str], Optional[str]]:
    """Return (event_type, text_or_none) from a segment event row."""
    # pandas Series (dict-like access)
    if hasattr(event, "get"):
        return str(event.get("type", "") or ""), str(event.get("text", "") or "")
    # dict
    if isinstance(event, dict):
        return str(event.get("type", "") or ""), str(event.get("text", "") or "")
    # attribute access (namedtuple / dataclass)
    ev_type = str(getattr(event, "type", "") or "")
    ev_text = str(getattr(event, "text", "") or "")
    return ev_type, ev_text


# ---------------------------------------------------------------------------
# Core mapping function
# ---------------------------------------------------------------------------

def map_segments_to_brain(
    predictions: np.ndarray,
    segments: list,
    region_indices: Optional[dict[str, np.ndarray]] = None,
    top_regions_per_tr: int = 5,
) -> ContentBrainMap:
    """Map TRIBE segments to brain responses.

    Parameters
    ----------
    predictions:
        Shape (n_trs, 20484) — raw TRIBE output at 2 Hz.
    segments:
        List of segment objects returned by TRIBE's predict().  May be shorter
        than n_trs if the last segment covers multiple TRs.
    region_indices:
        Optional {cluster_name: vertex_indices} from atlas.get_vertex_atlas().
        If provided, each ContentMoment will include the top activated clusters.
    top_regions_per_tr:
        How many top regions to store per TR.

    Returns
    -------
    ContentBrainMap with word activations, peak/weak moments.
    """
    n_trs = predictions.shape[0]
    n_verts = predictions.shape[1]
    moments: List[ContentMoment] = []

    # Accumulators for word-level statistics
    word_total: dict[str, float] = {}
    word_count: dict[str, int] = {}

    # Pre-compute region mean activations once per region (vectorised)
    precomputed_region_means: Optional[np.ndarray] = None
    region_name_list: list[str] = []

    if region_indices:
        region_name_list = list(region_indices.keys())
        region_means_per_tr: list[np.ndarray] = []
        for name in region_name_list:
            indices = region_indices[name]
            if len(indices) == 0:
                region_means_per_tr.append(np.zeros(n_trs))
            else:
                valid = indices[indices < n_verts]
                if len(valid) == 0:
                    region_means_per_tr.append(np.zeros(n_trs))
                else:
                    region_means_per_tr.append(np.abs(predictions[:, valid]).mean(axis=1))
        # Stack to (n_regions, n_trs)
        precomputed_region_means = np.stack(region_means_per_tr, axis=0)

    for i in range(n_trs):
        overall_act = float(np.abs(predictions[i]).mean())
        moment = ContentMoment(
            tr_index=i,
            timestamp_seconds=i * TRIBE_TR,
            overall_activation=overall_act,
        )

        # Extract events from segment
        if i < len(segments):
            for event in _safe_iter_events(segments[i]):
                ev_type, ev_text = _extract_event_info(event)

                if ev_type == "Word" and ev_text.strip():
                    word = ev_text.strip()
                    moment.words.append(word)
                    moment.has_speech = True

                    key = word.lower()
                    word_total[key] = word_total.get(key, 0.0) + overall_act
                    word_count[key] = word_count.get(key, 0) + 1

                elif ev_type in ("Video", "Image"):
                    moment.has_video = True

                elif ev_type == "Audio":
                    moment.has_audio = True

        # Top activated regions for this TR
        if precomputed_region_means is not None:
            region_scores_i = precomputed_region_means[:, i]   # (n_regions,)
            top_indices = np.argsort(region_scores_i)[::-1][:top_regions_per_tr]
            moment.top_regions = [
                {"name": region_name_list[j], "activation": round(float(region_scores_i[j]), 5)}
                for j in top_indices
            ]

        moments.append(moment)

    # Average word activations
    word_activations: dict[str, float] = {
        w: word_total[w] / word_count[w]
        for w in word_total
        if word_count.get(w, 0) > 0
    }

    # Sort moments by activation for peak / weak detection
    sorted_by_act = sorted(moments, key=lambda m: m.overall_activation, reverse=True)
    peaks = sorted_by_act[:5]
    weakspots = sorted_by_act[-5:]

    return ContentBrainMap(
        moments=moments,
        word_activations=word_activations,
        peak_moments=peaks,
        weak_moments=weakspots,
    )


# ---------------------------------------------------------------------------
# Convenience: speech-only timeline
# ---------------------------------------------------------------------------

def speech_activation_curve(brain_map: ContentBrainMap) -> List[tuple[float, float]]:
    """Return (timestamp, activation) for every TR that contains speech.

    Useful for overlaying speech activation on the timeline chart.
    """
    return [
        (m.timestamp_seconds, m.overall_activation)
        for m in brain_map.moments
        if m.has_speech
    ]
