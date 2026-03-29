"""Convert TRIBE brain predictions to marketing scores."""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List
from atlas import TRIBE_TR_SECONDS, MARKETING_REGIONS, get_vertex_atlas


@dataclass
class SecondScore:
    """Score for a single second of content."""
    timestamp: float
    attention: float      # 0-100 overall attention
    visual: float         # 0-100 visual cortex activation
    auditory: float       # 0-100 auditory cortex activation
    language: float       # 0-100 language processing
    decision: float       # 0-100 prefrontal (decision-making)
    emotion: float        # 0-100 default mode (self-reference/emotion)
    face_response: float  # 0-100 face detection response


@dataclass
class WeakMoment:
    start: float
    end: float
    reason: str
    recommendation: str
    severity: str  # "warning" | "critical"


@dataclass
class PeakMoment:
    start: float
    end: float
    reason: str
    use_case: str  # "hook" | "thumbnail" | "clip"


@dataclass
class ContentScore:
    """Full scoring result for a piece of content."""
    overall_score: int                          # 0-100
    duration_seconds: int
    per_second: List[SecondScore] = field(default_factory=list)

    # Region averages
    visual_avg: float = 0.0
    auditory_avg: float = 0.0
    language_avg: float = 0.0
    decision_avg: float = 0.0
    emotion_avg: float = 0.0

    # Modality contribution
    visual_pct: float = 0.0
    audio_pct: float = 0.0
    text_pct: float = 0.0

    # Moments
    weak_moments: List[WeakMoment] = field(default_factory=list)
    peak_moments: List[PeakMoment] = field(default_factory=list)

    # Hook analysis
    hook_score: float = 0.0  # first 3 seconds score
    hook_frame: int = 0       # best thumbnail frame (second)

    def to_dict(self) -> dict:
        return asdict(self)


def _region_activation(predictions: np.ndarray, region_key: str) -> np.ndarray:
    """Extract activation for a marketing region using real atlas mapping."""
    atlas = get_vertex_atlas()
    region_info = MARKETING_REGIONS.get(region_key, {})
    hcp_regions = region_info.get("hcp_regions", [])

    indices = []
    for reg in hcp_regions:
        if reg in atlas:
            indices.extend(atlas[reg])

    if not indices:
        return np.zeros(predictions.shape[0])

    indices = [i for i in indices if i < predictions.shape[1]]
    if not indices:
        return np.zeros(predictions.shape[0])

    return np.mean(predictions[:, indices], axis=1)


def _normalize_to_100(arr: np.ndarray) -> np.ndarray:
    """Normalize array to 0-100 scale using percentile scaling (robust to outliers)."""
    if arr.max() == arr.min():
        return np.full_like(arr, 50.0)
    p5, p95 = np.percentile(arr, [5, 95])
    if p95 == p5:
        return np.full_like(arr, 50.0)
    normalized = (arr - p5) / (p95 - p5) * 100
    return np.clip(normalized, 0, 100)


def score_content(predictions: np.ndarray, segments: list) -> ContentScore:
    """Convert raw TRIBE predictions to marketing scores.

    Args:
        predictions: shape (n_trs, ~20484) — raw TRIBE vertex output at 2 Hz
        segments: list of segment objects returned by TRIBE

    Returns:
        ContentScore with per-TR breakdown (timestamped in seconds), weak/peak
        moments, and aggregates.
    """
    n_trs = predictions.shape[0]
    duration_seconds = n_trs * TRIBE_TR_SECONDS

    # Extract per-region activations using real HCP-MMP1 atlas mapping
    visual = _normalize_to_100(_region_activation(predictions, "visual_processing"))
    auditory = _normalize_to_100(_region_activation(predictions, "auditory_processing"))
    language = _normalize_to_100(_region_activation(predictions, "language_comprehension"))
    decision = _normalize_to_100(_region_activation(predictions, "decision_making"))
    emotion = _normalize_to_100(_region_activation(predictions, "emotional_resonance"))
    face = _normalize_to_100(_region_activation(predictions, "face_recognition"))

    # Overall attention = weighted combination of cognitive systems
    attention = _normalize_to_100(
        0.25 * visual
        + 0.20 * auditory
        + 0.20 * language
        + 0.20 * decision
        + 0.15 * emotion
    )

    # Build per-TR scores with correct wall-clock timestamps
    per_second: List[SecondScore] = [
        SecondScore(
            timestamp=float(i) * TRIBE_TR_SECONDS,
            attention=float(attention[i]),
            visual=float(visual[i]),
            auditory=float(auditory[i]),
            language=float(language[i]),
            decision=float(decision[i]),
            emotion=float(emotion[i]),
            face_response=float(face[i]),
        )
        for i in range(n_trs)
    ]

    # Modality contribution — which brain systems are most active on average
    v_total = float(np.mean(visual))
    a_total = float(np.mean(auditory))
    t_total = float(np.mean(language))
    mod_sum = v_total + a_total + t_total
    if mod_sum > 0:
        v_pct = v_total / mod_sum * 100
        a_pct = a_total / mod_sum * 100
        t_pct = t_total / mod_sum * 100
    else:
        v_pct = a_pct = t_pct = 33.3

    # Find weak moments: attention below 40 for 2+ consecutive TRs
    weak_moments: List[WeakMoment] = []
    i = 0
    while i < n_trs:
        if attention[i] < 40:
            start = i
            while i < n_trs and attention[i] < 40:
                i += 1
            end = i
            if end - start >= 2:
                visual_drop = np.mean(visual[start:end]) < 30
                audio_drop = np.mean(auditory[start:end]) < 30
                decision_drop = np.mean(decision[start:end]) < 30
                duration_span = (end - start) * TRIBE_TR_SECONDS

                if visual_drop and not audio_drop:
                    reason = f"Visual cortex flat for {duration_span:.1f}s. No scene change."
                    rec = "Add a visual cut, face, or scene change."
                elif decision_drop:
                    reason = "Prefrontal drops — nothing to evaluate."
                    rec = "Add a question, statistic, or decision prompt."
                else:
                    reason = f"Overall attention below threshold for {duration_span:.1f}s."
                    rec = "Shorten this section or add engagement triggers."

                weak_moments.append(WeakMoment(
                    start=float(start) * TRIBE_TR_SECONDS,
                    end=float(end) * TRIBE_TR_SECONDS,
                    reason=reason,
                    recommendation=rec,
                    severity="critical" if duration_span >= 4.0 else "warning",
                ))
        else:
            i += 1

    # Find peak moments: attention above 80 for 2+ consecutive TRs
    peak_moments: List[PeakMoment] = []
    i = 0
    while i < n_trs:
        if attention[i] > 80:
            start = i
            while i < n_trs and attention[i] > 80:
                i += 1
            end = i
            if end - start >= 2:
                start_secs = float(start) * TRIBE_TR_SECONDS
                end_secs = float(end) * TRIBE_TR_SECONDS
                if start_secs <= 5.0:
                    use_case = "hook"
                    reason = "Strong opening — high combined activation."
                elif face[start:end].mean() > 70:
                    use_case = "thumbnail"
                    reason = "Face + attention peak — ideal thumbnail frame."
                else:
                    use_case = "clip"
                    reason = "Engagement spike — use as short-form clip."

                peak_moments.append(PeakMoment(
                    start=start_secs,
                    end=end_secs,
                    reason=reason,
                    use_case=use_case,
                ))
        else:
            i += 1

    # Hook analysis: first 3 real seconds = first int(3 / TRIBE_TR_SECONDS) TRs
    hook_trs = int(3.0 / TRIBE_TR_SECONDS)
    hook_score = float(np.mean(attention[:min(hook_trs, n_trs)]))
    # Best thumbnail frame: argmax of face in first 5 seconds
    face_trs = int(5.0 / TRIBE_TR_SECONDS)
    hook_frame = int(np.argmax(face[:min(face_trs, n_trs)]))

    overall = int(np.mean(attention))

    return ContentScore(
        overall_score=overall,
        duration_seconds=int(duration_seconds),
        per_second=per_second,
        visual_avg=float(np.mean(visual)),
        auditory_avg=float(np.mean(auditory)),
        language_avg=float(np.mean(language)),
        decision_avg=float(np.mean(decision)),
        emotion_avg=float(np.mean(emotion)),
        visual_pct=v_pct,
        audio_pct=a_pct,
        text_pct=t_pct,
        weak_moments=weak_moments,
        peak_moments=peak_moments,
        hook_score=hook_score,
        hook_frame=hook_frame,
    )
