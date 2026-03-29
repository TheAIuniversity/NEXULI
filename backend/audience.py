"""
Audience Archetypes — use TRIBE's 25 subject heads as audience proxies.

TRIBE was trained on 25 subjects across 4 studies:
- Algonauts (4 subjects): trained on Friends + movies → visual-dominant processors
- Wen2017 (3 subjects): trained on long videos → sustained visual attention
- Lahner2024 (10 subjects): trained on short video clips → quick visual processing
- Lebel2023 (8 subjects): trained on spoken narratives → audio/language processors

Each subject learned a different brain-to-content mapping.
Using individual subjects as audience proxies gives us:
- "How would a visual learner respond to this?"
- "How would an audio learner respond to this?"
- Confidence intervals (high inter-subject variance = content affects people differently)

Usage
-----
    from audience import analyze_audience_from_subjects, ARCHETYPES

    # per_subject_predictions from TribeEngine with run_per_subject=True
    analysis = analyze_audience_from_subjects(per_subject_predictions)
    print(analysis.to_dict())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Subject → archetype mapping
# ---------------------------------------------------------------------------

@dataclass
class SubjectArchetype:
    """Maps a TRIBE training subject to an audience archetype."""
    subject_id: str
    study: str
    archetype: str
    description: str
    primary_modality: str      # "visual" or "audio"
    training_hours: float
    reliability: str           # "high" (>15 h data), "medium" (6-15 h), "low" (<6 h)


# The 25 subjects mapped to audience archetypes.
SUBJECT_ARCHETYPES: list[SubjectArchetype] = [
    # ----------------------------------------------------------------
    # Algonauts2025Bold — Friends TV + movie clips, ~80 h / subject
    # Visual-dominant; trained on rich social/face content.
    # ----------------------------------------------------------------
    SubjectArchetype("sub-01", "Algonauts2025Bold", "Visual Engager",
                     "Responds strongly to visual narrative and faces", "visual", 80.0, "high"),
    SubjectArchetype("sub-02", "Algonauts2025Bold", "Visual Engager",
                     "Visual narrative processor with high face sensitivity", "visual", 80.0, "high"),
    SubjectArchetype("sub-03", "Algonauts2025Bold", "Visual Engager",
                     "Strong visual cortex responses to dynamic scenes", "visual", 80.0, "high"),
    SubjectArchetype("sub-05", "Algonauts2025Bold", "Visual Engager",
                     "Visual-dominant with moderate language co-activation", "visual", 80.0, "high"),

    # ----------------------------------------------------------------
    # Wen2017 — long-form video, ~6 h / subject
    # Sustained visual processors; deep engagement over time.
    # ----------------------------------------------------------------
    SubjectArchetype("subject1", "Wen2017", "Sustained Viewer",
                     "Deep engagement with long-form video content", "visual", 6.0, "medium"),
    SubjectArchetype("subject2", "Wen2017", "Sustained Viewer",
                     "Sustained visual attention, less language processing", "visual", 6.0, "medium"),
    SubjectArchetype("subject3", "Wen2017", "Sustained Viewer",
                     "Long-form visual processing with gradual engagement", "visual", 6.0, "medium"),

    # ----------------------------------------------------------------
    # Lahner2024Bold — short video clips, ~6 h / subject
    # Fast visual processors; decide in 1-3 seconds.
    # ----------------------------------------------------------------
    SubjectArchetype("1",  "Lahner2024Bold", "Quick Scanner", "Fast visual processing of short content",   "visual", 6.0, "medium"),
    SubjectArchetype("2",  "Lahner2024Bold", "Quick Scanner", "Rapid scene categorisation",                "visual", 6.0, "medium"),
    SubjectArchetype("3",  "Lahner2024Bold", "Quick Scanner", "Quick visual assessment",                   "visual", 6.0, "medium"),
    SubjectArchetype("4",  "Lahner2024Bold", "Quick Scanner", "Fast visual processor",                     "visual", 6.0, "medium"),
    SubjectArchetype("5",  "Lahner2024Bold", "Quick Scanner", "Short-form visual processing",              "visual", 6.0, "medium"),
    SubjectArchetype("6",  "Lahner2024Bold", "Quick Scanner", "Quick visual scanner",                      "visual", 6.0, "medium"),
    SubjectArchetype("7",  "Lahner2024Bold", "Quick Scanner", "Rapid visual assessment",                   "visual", 6.0, "medium"),
    SubjectArchetype("8",  "Lahner2024Bold", "Quick Scanner", "Fast scene processor",                      "visual", 6.0, "medium"),
    SubjectArchetype("9",  "Lahner2024Bold", "Quick Scanner", "Quick visual evaluator",                    "visual", 6.0, "medium"),
    SubjectArchetype("10", "Lahner2024Bold", "Quick Scanner", "Short-form visual scanner",                 "visual", 6.0, "medium"),

    # ----------------------------------------------------------------
    # Lebel2023Bold — spoken narratives (audiobooks / podcasts)
    # Audio/language dominant processors; respond to voice and story.
    # ----------------------------------------------------------------
    SubjectArchetype("UTS01", "Lebel2023Bold", "Audio Learner",
                     "Deep audio processing, strong narrative comprehension", "audio", 17.2, "high"),
    SubjectArchetype("UTS02", "Lebel2023Bold", "Audio Learner",
                     "Audio-dominant with rich language activation", "audio", 18.0, "high"),
    SubjectArchetype("UTS03", "Lebel2023Bold", "Audio Learner",
                     "Strong audio/language co-processing", "audio", 17.5, "high"),
    SubjectArchetype("UTS04", "Lebel2023Bold", "Audio Learner",
                     "Narrative-driven audio processor", "audio", 8.0, "medium"),
    SubjectArchetype("UTS05", "Lebel2023Bold", "Audio Learner",
                     "Audio comprehension specialist", "audio", 8.0, "medium"),
    SubjectArchetype("UTS06", "Lebel2023Bold", "Audio Learner",
                     "Audio/language processor", "audio", 8.0, "medium"),
    SubjectArchetype("UTS07", "Lebel2023Bold", "Audio Learner",
                     "Narrative audio processor", "audio", 8.0, "medium"),
    SubjectArchetype("UTS08", "Lebel2023Bold", "Audio Learner",
                     "Audio-dominant learner", "audio", 8.0, "medium"),
]

# Lookup: subject_id → SubjectArchetype
SUBJECT_LOOKUP: dict[str, SubjectArchetype] = {s.subject_id: s for s in SUBJECT_ARCHETYPES}

# Grouped by archetype name
ARCHETYPES: dict[str, dict] = {
    "Visual Engager": {
        "description": (
            "Responds best to face-forward video with visual narrative. "
            "Friends / movie watchers. Strong face, scene, and emotion processing."
        ),
        "subjects": [s for s in SUBJECT_ARCHETYPES if s.archetype == "Visual Engager"],
        "best_content": "Video ads with faces, visual storytelling, product demos",
        "modality": "visual",
    },
    "Audio Learner": {
        "description": (
            "Responds best to voiceover, podcasts, audio-driven content. "
            "Story listeners. Deep language and narrative processing."
        ),
        "subjects": [s for s in SUBJECT_ARCHETYPES if s.archetype == "Audio Learner"],
        "best_content": "Podcast clips, voiceover ads, audio testimonials",
        "modality": "audio",
    },
    "Sustained Viewer": {
        "description": (
            "Engages deeply with long-form video. Patient; builds engagement over time. "
            "Best for explainers, webinars, and documentary-style content."
        ),
        "subjects": [s for s in SUBJECT_ARCHETYPES if s.archetype == "Sustained Viewer"],
        "best_content": "YouTube videos, webinars, long-form explainers",
        "modality": "visual",
    },
    "Quick Scanner": {
        "description": (
            "Fast visual processor. Decides in 1-3 seconds. Short-form native. "
            "Hook must land in the first second."
        ),
        "subjects": [s for s in SUBJECT_ARCHETYPES if s.archetype == "Quick Scanner"],
        "best_content": "TikTok, Reels, Stories, short-form video",
        "modality": "visual",
    },
}


# ---------------------------------------------------------------------------
# Analysis result
# ---------------------------------------------------------------------------

@dataclass
class AudienceAnalysis:
    """Per-archetype analysis of content."""
    archetype_scores: dict    # {archetype_name: {score, variance, n_subjects, modality, recommendation}}
    best_archetype: str
    worst_archetype: str
    confidence: float         # 0-1; low variance across archetypes = consistent response
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "archetype_scores": self.archetype_scores,
            "best_archetype": self.best_archetype,
            "worst_archetype": self.worst_archetype,
            "confidence": round(self.confidence, 2),
            "recommendation": self.recommendation,
        }

    def best_platform(self) -> str:
        """Quick platform recommendation based on best archetype."""
        platform_map = {
            "Visual Engager": "YouTube / Instagram video",
            "Audio Learner":  "Podcast / audio ad / LinkedIn",
            "Sustained Viewer": "YouTube / webinar",
            "Quick Scanner": "TikTok / Instagram Reels / Stories",
        }
        return platform_map.get(self.best_archetype, "mixed platforms")


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

def analyze_audience_from_subjects(
    per_subject_predictions: dict[str, np.ndarray],
) -> AudienceAnalysis:
    """Analyse content response per audience archetype from per-subject predictions.

    Parameters
    ----------
    per_subject_predictions:
        {subject_id: predictions_array} where each array has shape
        (n_trs, 20484) — raw TRIBE output for that subject head.

    Returns
    -------
    AudienceAnalysis with per-archetype scores and deployment recommendation.
    """
    archetype_scores: dict[str, dict] = {}

    for archetype_name, arch_info in ARCHETYPES.items():
        subject_means: list[float] = []

        for subj in arch_info["subjects"]:
            if subj.subject_id in per_subject_predictions:
                preds = per_subject_predictions[subj.subject_id]
                # Weight high-reliability subjects more
                weight = 1.5 if subj.reliability == "high" else 1.0
                subject_means.append(
                    float(np.abs(preds).mean()) * weight
                )

        if subject_means:
            avg_score = float(np.mean(subject_means))
            variance = float(np.std(subject_means))
            archetype_scores[archetype_name] = {
                "score": round(avg_score * 100, 1),
                "variance": round(variance * 100, 1),
                "n_subjects": len(subject_means),
                "modality": arch_info["modality"],
                "recommendation": arch_info["best_content"],
            }

    if not archetype_scores:
        return AudienceAnalysis(
            archetype_scores={},
            best_archetype="unknown",
            worst_archetype="unknown",
            confidence=0.0,
            recommendation="No subject data available — run with per_subject=True.",
        )

    best = max(archetype_scores, key=lambda k: archetype_scores[k]["score"])
    worst = min(archetype_scores, key=lambda k: archetype_scores[k]["score"])

    all_scores = [v["score"] for v in archetype_scores.values()]
    spread = float(np.std(all_scores))
    # High confidence = consistent (low spread), low confidence = wildly different responses
    confidence = max(0.0, 1.0 - spread / 50.0)

    best_score = archetype_scores[best]["score"]
    worst_score = archetype_scores[worst]["score"]

    if confidence > 0.7:
        rec = (
            f"Content performs consistently across all audiences (low variance). "
            f"Safe to deploy broadly without audience targeting."
        )
    elif best_score > worst_score * 1.5:
        rec = (
            f"{best} responds {best_score:.0f}% vs {worst_score:.0f}% for {worst}. "
            f"Strong skew — prioritise creative for {best}. "
            f"Best platform: {ARCHETYPES[best]['best_content']}."
        )
    else:
        rec = (
            f"{best} responds best ({best_score:.0f}%). "
            f"Moderate variation — run A/B test per segment. "
            f"Recommend starting with: {ARCHETYPES[best]['best_content']}."
        )

    return AudienceAnalysis(
        archetype_scores=archetype_scores,
        best_archetype=best,
        worst_archetype=worst,
        confidence=confidence,
        recommendation=rec,
    )


# ---------------------------------------------------------------------------
# Reliability weighting helper
# ---------------------------------------------------------------------------

def weighted_ensemble_predictions(
    per_subject_predictions: dict[str, np.ndarray],
) -> np.ndarray:
    """Compute a reliability-weighted ensemble prediction.

    High-reliability subjects (>15 h training data) are weighted 1.5×.
    Returns shape (n_trs, 20484) — the weighted mean across subjects.
    """
    weights: list[float] = []
    arrays: list[np.ndarray] = []

    for subj_id, preds in per_subject_predictions.items():
        subj = SUBJECT_LOOKUP.get(subj_id)
        w = 1.5 if subj and subj.reliability == "high" else 1.0
        weights.append(w)
        arrays.append(preds)

    if not arrays:
        raise ValueError("per_subject_predictions is empty")

    w_arr = np.array(weights)
    stacked = np.stack(arrays, axis=0)   # (n_subjects, n_trs, n_vertices)
    return np.average(stacked, axis=0, weights=w_arr)
