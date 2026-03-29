"""
Fine-Tuning Configuration — prepare for training custom heads on TRIBE's backbone.

TRIBE supports:
1. resize_subject_layer  — create new subject heads initialised from the average
   of existing subjects (SVD-based weight transfer if dimension changes).
2. freeze_backbone       — freeze the transformer, only train the prediction head.
   This works because TRIBE's backbone is a general multimodal encoder; only the
   final linear projection needs to be specialised per audience / metric.

This module prepares config + data collection for when the Mac Mini arrives.
No PyTorch dependency — everything here is pure Python / stdlib.

Usage
-----
    from finetune import FinetuneConfig, PairedDataCollector, PairedSample

    config = FinetuneConfig(target_type="ctr", n_outputs=1)
    print(config.to_dict())

    collector = PairedDataCollector()
    collector.add_sample(PairedSample(
        content_id="ad_001", content_path="/path/ad.mp4",
        tribe_score=72.3, ctr=0.048, platform="instagram", audience_segment="quick_scanner",
    ))
    print(collector.readiness_report())
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Fine-tuning config
# ---------------------------------------------------------------------------

@dataclass
class FinetuneConfig:
    """Configuration for fine-tuning TRIBE on custom engagement data.

    Recommended workflow
    --------------------
    1. Collect 100+ paired samples (content + real metric) via PairedDataCollector.
    2. Run baseline TRIBE scores on each piece of content.
    3. Set freeze_backbone=True (avoids catastrophic forgetting of the backbone).
    4. Train: one new linear "audience head" per custom subject slot.
    5. Validate: correlate TRIBE-finetuned predictions with held-out real metrics.
    """

    # What to train
    freeze_backbone: bool = True        # Keep transformer frozen; only train output head
    resize_subject_layer: bool = True   # Create new subject heads
    n_new_subjects: int = 1             # Number of new "audience" head slots

    # New prediction target
    target_type: str = "engagement"     # "engagement" | "conversion" | "watch_time" | "ctr"
    n_outputs: int = 1                  # Number of output metrics to predict

    # Training hyperparameters (sensible defaults for frozen-backbone fine-tuning)
    learning_rate: float = 1e-4
    epochs: int = 15
    batch_size: int = 16
    warmup_pct: float = 0.1            # Fraction of steps used for LR warmup

    # Data requirements
    min_samples: int = 100              # Minimum paired (content, metric) samples needed
    validation_split: float = 0.2

    # What data format to collect
    required_data: List[str] = field(default_factory=lambda: [
        "content_file (video / audio / text)",
        "tribe_score  (run through TRIBE first to get the baseline brain score)",
        "real_metric  (CTR, conversion rate, watch time, engagement rate, etc.)",
        "audience_segment (optional — enables per-segment heads)",
    ])

    def to_dict(self) -> dict:
        return {
            "freeze_backbone": self.freeze_backbone,
            "resize_subject_layer": self.resize_subject_layer,
            "n_new_subjects": self.n_new_subjects,
            "target_type": self.target_type,
            "n_outputs": self.n_outputs,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "warmup_pct": self.warmup_pct,
            "min_samples": self.min_samples,
            "validation_split": self.validation_split,
            "required_data": self.required_data,
            "status": self._status(),
        }

    def _status(self) -> str:
        return (
            "Ready to configure. "
            "Requires Mac Mini with Apple Silicon GPU + "
            f"at least {self.min_samples} paired (content, {self.target_type}) samples."
        )

    def training_script_hint(self) -> str:
        """Print the tribev2 fine-tuning command pattern."""
        return (
            "python -m tribev2.finetune \\\n"
            f"  --target {self.target_type} \\\n"
            f"  --n_subjects {self.n_new_subjects} \\\n"
            f"  --freeze_backbone {str(self.freeze_backbone).lower()} \\\n"
            f"  --lr {self.learning_rate} \\\n"
            f"  --epochs {self.epochs} \\\n"
            f"  --batch_size {self.batch_size}"
        )


# ---------------------------------------------------------------------------
# Paired sample — one content piece + one real-world metric observation
# ---------------------------------------------------------------------------

@dataclass
class PairedSample:
    """One training sample: content + TRIBE score + real-world performance."""

    content_id: str                     # Unique identifier (e.g. "ad_video_001")
    content_path: str                   # Path to original file

    # TRIBE output (fill after running through TribeEngine)
    tribe_predictions_path: Optional[str] = None   # Path to saved .npy predictions
    tribe_score: float = 0.0            # Overall 0-100 attention score
    tribe_hook_score: float = 0.0       # First-3-second hook score

    # Real-world metrics — fill after deployment and measurement window
    ctr: Optional[float] = None                     # Click-through rate (0-1)
    conversion_rate: Optional[float] = None         # Conversion rate (0-1)
    watch_time_seconds: Optional[float] = None      # Average watch time
    engagement_rate: Optional[float] = None         # Likes+comments / impressions
    custom_metric: Optional[float] = None           # Any other metric

    # Metadata
    platform: str = ""                  # "tiktok", "instagram", "youtube", "email", etc.
    audience_segment: str = ""          # "quick_scanner", "audio_learner", etc.
    content_type: str = ""              # "video_ad", "story", "podcast_clip", etc.

    deployed_at: Optional[float] = None           # Unix timestamp
    metrics_collected_at: Optional[float] = None  # Unix timestamp

    @property
    def is_complete(self) -> bool:
        """True if sample has both TRIBE score AND at least one real metric."""
        has_tribe = self.tribe_score > 0
        has_metric = any([
            self.ctr is not None,
            self.conversion_rate is not None,
            self.watch_time_seconds is not None,
            self.engagement_rate is not None,
            self.custom_metric is not None,
        ])
        return has_tribe and has_metric

    @property
    def primary_metric(self) -> Optional[float]:
        """Return the first available real metric."""
        for v in [self.ctr, self.conversion_rate, self.engagement_rate, self.custom_metric]:
            if v is not None:
                return v
        return None

    def to_dict(self) -> dict:
        return {
            "content_id": self.content_id,
            "content_path": self.content_path,
            "tribe_score": self.tribe_score,
            "tribe_hook_score": self.tribe_hook_score,
            "ctr": self.ctr,
            "conversion_rate": self.conversion_rate,
            "watch_time_seconds": self.watch_time_seconds,
            "engagement_rate": self.engagement_rate,
            "custom_metric": self.custom_metric,
            "platform": self.platform,
            "audience_segment": self.audience_segment,
            "content_type": self.content_type,
            "is_complete": self.is_complete,
        }


# ---------------------------------------------------------------------------
# Paired data collector
# ---------------------------------------------------------------------------

class PairedDataCollector:
    """Collect paired (TRIBE score, real performance) data for fine-tuning.

    Typical workflow
    ----------------
    1. Score content with TribeEngine → tribe_score.
    2. Deploy content.
    3. After measurement window, add real metrics with update_metrics().
    4. Call readiness_report() to see how close you are to 100 samples.
    """

    def __init__(self, target_samples: int = 100) -> None:
        self.samples: List[PairedSample] = []
        self.target_samples = target_samples

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_sample(self, sample: PairedSample) -> None:
        self.samples.append(sample)

    def update_metrics(
        self,
        content_id: str,
        ctr: Optional[float] = None,
        conversion_rate: Optional[float] = None,
        watch_time_seconds: Optional[float] = None,
        engagement_rate: Optional[float] = None,
        custom_metric: Optional[float] = None,
    ) -> bool:
        """Update real metrics for an existing sample.  Returns True if found."""
        for sample in self.samples:
            if sample.content_id == content_id:
                if ctr is not None:
                    sample.ctr = ctr
                if conversion_rate is not None:
                    sample.conversion_rate = conversion_rate
                if watch_time_seconds is not None:
                    sample.watch_time_seconds = watch_time_seconds
                if engagement_rate is not None:
                    sample.engagement_rate = engagement_rate
                if custom_metric is not None:
                    sample.custom_metric = custom_metric
                sample.metrics_collected_at = time.time()
                return True
        return False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_complete_samples(self) -> List[PairedSample]:
        """Samples that have both TRIBE scores AND real metrics."""
        return [s for s in self.samples if s.is_complete]

    def get_by_platform(self, platform: str) -> List[PairedSample]:
        return [s for s in self.samples if s.platform.lower() == platform.lower()]

    def get_by_segment(self, segment: str) -> List[PairedSample]:
        return [s for s in self.samples if s.audience_segment.lower() == segment.lower()]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def readiness_report(self) -> dict:
        """How close are we to having enough data to fine-tune?"""
        all_samples = self.samples
        complete = self.get_complete_samples()
        n_complete = len(complete)
        target = self.target_samples

        platforms = sorted(set(s.platform for s in complete if s.platform))
        segments = sorted(set(s.audience_segment for s in complete if s.audience_segment))
        content_types = sorted(set(s.content_type for s in complete if s.content_type))

        # Tribe score vs metric correlation (only if we have enough data)
        correlation: Optional[float] = None
        if n_complete >= 10:
            scores = [s.tribe_score for s in complete]
            metrics = [s.primary_metric for s in complete if s.primary_metric is not None]
            if len(metrics) >= 10:
                try:
                    import numpy as np
                    s_arr = [s.tribe_score for s in complete if s.primary_metric is not None]
                    m_arr = [s.primary_metric for s in complete if s.primary_metric is not None]
                    if len(s_arr) >= 10:
                        corr = float(
                            (
                                (len(s_arr) * sum(a * b for a, b in zip(s_arr, m_arr)))
                                - sum(s_arr) * sum(m_arr)
                            )
                            / (
                                ((len(s_arr) * sum(a**2 for a in s_arr) - sum(s_arr)**2) ** 0.5)
                                * ((len(s_arr) * sum(b**2 for b in m_arr) - sum(m_arr)**2) ** 0.5)
                                + 1e-10
                            )
                        )
                        correlation = round(corr, 3)
                except Exception:
                    pass

        return {
            "total_samples": len(all_samples),
            "complete_samples": n_complete,
            "incomplete_samples": len(all_samples) - n_complete,
            "target_samples": target,
            "ready_to_finetune": n_complete >= target,
            "samples_needed": max(0, target - n_complete),
            "progress_pct": round(min(n_complete / target * 100, 100), 1),
            "platforms": platforms,
            "segments": segments,
            "content_types": content_types,
            "tribe_vs_metric_correlation": correlation,
            "next_step": (
                f"Collect {max(0, target - n_complete)} more complete samples."
                if n_complete < target
                else "Ready to fine-tune. Run FinetuneConfig.training_script_hint()."
            ),
        }
