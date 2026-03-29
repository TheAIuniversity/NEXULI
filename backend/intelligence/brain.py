"""
Evolving Agent Brain — central intelligence that learns from TRIBE scores + real performance.
Pattern stolen from goviralbitch's agent-brain.json architecture.
"""

import copy
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

BRAIN_PATH = settings.db_path.parent / "brain.json"

DEFAULT_BRAIN = {
    "version": 1,
    "updated_at": 0,

    # Learning weights — these evolve based on what actually performs
    # Each weight starts at 1.0 and adjusts 0.1-5.0 based on correlation with real outcomes
    "learning_weights": {
        "visual_cortex": 1.0,      # How much visual engagement predicts real performance
        "auditory_cortex": 1.0,    # How much audio engagement predicts real performance
        "language_areas": 1.0,     # How much language processing predicts real performance
        "prefrontal": 1.0,         # How much decision activation predicts real performance
        "default_mode": 1.0,       # How much emotional resonance predicts real performance
        "hook_strength": 1.0,      # How much first-3-seconds score predicts real performance
    },

    # Hook pattern performance — tracks which hook types score highest
    "hook_patterns": {
        "face_first": {"tribe_avg": 0, "real_avg": 0, "count": 0},
        "question_open": {"tribe_avg": 0, "real_avg": 0, "count": 0},
        "pattern_interrupt": {"tribe_avg": 0, "real_avg": 0, "count": 0},
        "contrast_statement": {"tribe_avg": 0, "real_avg": 0, "count": 0},
        "vulnerable_confession": {"tribe_avg": 0, "real_avg": 0, "count": 0},
        "specificity": {"tribe_avg": 0, "real_avg": 0, "count": 0},
    },

    # Modality insights — learned from TRIBE scores
    "modality_insights": {
        "visual_dominant_avg_score": 0,   # avg score when visual > 50%
        "audio_dominant_avg_score": 0,    # avg score when audio > 50%
        "text_dominant_avg_score": 0,     # avg score when text > 50%
        "balanced_avg_score": 0,          # avg score when no modality > 50%
    },

    # Per-modality item counters — used for correct rolling averages
    "modality_counts": {
        "visual_dominant": 0,
        "audio_dominant": 0,
        "text_dominant": 0,
        "balanced": 0,
    },

    # Performance benchmarks — rolling averages from scored content
    "benchmarks": {
        "overall_score_avg": 0,
        "hook_score_avg": 0,
        "weak_moments_avg": 0,
        "peak_moments_avg": 0,
        "content_scored": 0,
    },

    # Competitor intelligence
    "competitors": {},  # name -> {avg_score, last_scanned, content_count}

    # Discovered patterns (from learner agent)
    "patterns": [],  # list of {pattern, confidence, discovered_at}
}


class AgentBrain:
    """Singleton evolving brain that all agents read from and the learner writes to."""

    _instance: Optional["AgentBrain"] = None
    _data: dict = None

    @classmethod
    def get(cls) -> "AgentBrain":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load()
        return cls._instance

    def _load(self):
        if BRAIN_PATH.exists():
            try:
                self._data = json.loads(BRAIN_PATH.read_text())
                logger.info(
                    f"Brain loaded: v{self._data.get('version', 0)}, "
                    f"{self._data['benchmarks']['content_scored']} items scored"
                )
            except Exception as e:
                logger.warning(f"Brain corrupted, resetting: {e}")
                self._data = copy.deepcopy(DEFAULT_BRAIN)
        else:
            self._data = copy.deepcopy(DEFAULT_BRAIN)
            self._save()

    def _save(self):
        self._data["updated_at"] = time.time()
        BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
        BRAIN_PATH.write_text(json.dumps(self._data, indent=2))

    @property
    def data(self) -> dict:
        return self._data

    @property
    def weights(self) -> dict:
        return self._data["learning_weights"]

    def update_from_score(self, score_result: dict):
        """Update brain benchmarks from a new TRIBE score."""
        b = self._data["benchmarks"]
        n = b["content_scored"]

        # Rolling averages
        b["overall_score_avg"] = (b["overall_score_avg"] * n + score_result["overall_score"]) / (n + 1)
        b["hook_score_avg"] = (b["hook_score_avg"] * n + score_result.get("hook_score", 0)) / (n + 1)
        b["weak_moments_avg"] = (b["weak_moments_avg"] * n + len(score_result.get("weak_moments", []))) / (n + 1)
        b["peak_moments_avg"] = (b["peak_moments_avg"] * n + len(score_result.get("peak_moments", []))) / (n + 1)
        b["content_scored"] = n + 1

        # Update modality insights using per-modality counters (HIGH-8 fix)
        v_pct = score_result.get("visual_pct", 33)
        a_pct = score_result.get("audio_pct", 33)
        t_pct = score_result.get("text_pct", 33)
        overall = score_result["overall_score"]

        mi = self._data["modality_insights"]
        mc = self._data["modality_counts"]
        if v_pct > 50:
            mi["visual_dominant_avg_score"] = _rolling_avg(
                mi["visual_dominant_avg_score"], overall, mc["visual_dominant"]
            )
            mc["visual_dominant"] += 1
        elif a_pct > 50:
            mi["audio_dominant_avg_score"] = _rolling_avg(
                mi["audio_dominant_avg_score"], overall, mc["audio_dominant"]
            )
            mc["audio_dominant"] += 1
        elif t_pct > 50:
            mi["text_dominant_avg_score"] = _rolling_avg(
                mi["text_dominant_avg_score"], overall, mc["text_dominant"]
            )
            mc["text_dominant"] += 1
        else:
            mi["balanced_avg_score"] = _rolling_avg(
                mi["balanced_avg_score"], overall, mc["balanced"]
            )
            mc["balanced"] += 1

        self._save()

    def update_weights(self, real_performance: dict, tribe_score: dict):
        """Adjust learning weights based on real performance vs TRIBE prediction.

        This is the core learning loop: when we get real campaign data,
        correlate it with TRIBE brain region scores to learn which regions
        actually predict performance.

        real_performance: {"ctr": float, "conversion": float, "watch_time": float}
        tribe_score: full TRIBE score result
        """
        # Simple gradient: if a region was high and performance was high, increase weight
        # If a region was high but performance was low, decrease weight
        performance_signal = real_performance.get("ctr", 0) + real_performance.get("conversion", 0)

        region_map = {
            "visual_cortex": tribe_score.get("visual_avg", 50),
            "auditory_cortex": tribe_score.get("auditory_avg", 50),
            "language_areas": tribe_score.get("language_avg", 50),
            "prefrontal": tribe_score.get("decision_avg", 50),
            "default_mode": tribe_score.get("emotion_avg", 50),
            "hook_strength": tribe_score.get("hook_score", 50),
        }

        weights = self._data["learning_weights"]
        learning_rate = 0.05

        for region, activation in region_map.items():
            # Normalized activation (0-1)
            norm_activation = activation / 100.0
            # Adjust weight toward correlation
            if performance_signal > 0.5:  # Good performance
                weights[region] = min(5.0, weights[region] + learning_rate * norm_activation)
            else:  # Poor performance
                weights[region] = max(0.1, weights[region] - learning_rate * norm_activation)

        self._save()
        logger.info(f"Brain weights updated: {weights}")

    def add_pattern(self, pattern: str, confidence: float):
        """Add a discovered pattern to the brain."""
        self._data["patterns"].append({
            "pattern": pattern,
            "confidence": confidence,
            "discovered_at": time.time(),
        })
        # Keep top 100 by confidence
        self._data["patterns"] = sorted(
            self._data["patterns"],
            key=lambda p: p["confidence"],
            reverse=True,
        )[:100]
        self._save()

    def update_competitor(self, name: str, avg_score: float, content_count: int):
        """Update competitor intelligence."""
        self._data["competitors"][name] = {
            "avg_score": avg_score,
            "content_count": content_count,
            "last_scanned": time.time(),
        }
        self._save()

    def set_weights(self, weights: dict):
        """Overwrite learning weights with validated values.

        Each weight must be a float in [0.1, 5.0]. Unknown keys are ignored so
        callers can pass a partial update.

        Raises:
            ValueError: If any provided value is outside the allowed range.
        """
        valid_keys = set(self._data["learning_weights"].keys())
        for key, value in weights.items():
            if key not in valid_keys:
                continue
            if not isinstance(value, (int, float)):
                raise ValueError(f"Weight for '{key}' must be numeric, got {type(value)}")
            if not (0.1 <= float(value) <= 5.0):
                raise ValueError(
                    f"Weight for '{key}' must be in [0.1, 5.0], got {value}"
                )
            self._data["learning_weights"][key] = float(value)
        self._save()
        logger.info(f"Brain weights set manually: {self._data['learning_weights']}")

    def get_creative_guidelines(self) -> dict:
        """Generate creative guidelines based on current brain state."""
        weights = self._data["learning_weights"]
        mi = self._data["modality_insights"]

        # Find strongest weight
        strongest = max(weights, key=weights.get)

        # Find best modality mix
        modality_scores = {
            "visual_dominant": mi["visual_dominant_avg_score"],
            "audio_dominant": mi["audio_dominant_avg_score"],
            "text_dominant": mi["text_dominant_avg_score"],
            "balanced": mi["balanced_avg_score"],
        }
        best_modality = (
            max(modality_scores, key=modality_scores.get)
            if any(modality_scores.values())
            else "balanced"
        )

        return {
            "focus_region": strongest,
            "focus_weight": weights[strongest],
            "recommended_modality_mix": best_modality,
            "avg_score_to_beat": self._data["benchmarks"]["overall_score_avg"],
            "avg_hook_to_beat": self._data["benchmarks"]["hook_score_avg"],
            "top_patterns": self._data["patterns"][:5],
        }


def _rolling_avg(current: float, new_value: float, count: int) -> float:
    if count == 0:
        return new_value
    return (current * count + new_value) / (count + 1)
