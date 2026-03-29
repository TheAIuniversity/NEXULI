"""
Cross-Platform Engagement Normalization.
Pattern stolen from goviralbitch's log1p engagement scoring.
"""

import math
from dataclasses import dataclass


@dataclass
class EngagementScore:
    """Normalized engagement score for cross-platform comparison."""
    platform: str
    raw_metrics: dict
    engagement_score: float   # 0-100 normalized
    relevance_score: float    # 0-100
    recency_score: float      # 0-100
    overall_score: float      # weighted combo


def normalize_engagement(
    platform: str,
    metrics: dict,
    relevance: float = 50,
    recency: float = 50,
) -> EngagementScore:
    """Normalize engagement metrics across platforms using log1p scaling.

    Platform-specific formulas from goviralbitch:
    - Reddit: 55% score + 40% comments + 5% upvote_ratio
    - Twitter/X: 55% likes + 25% reposts + 15% replies + 5% quotes
    - YouTube: 50% views + 35% likes + 15% comments
    - LinkedIn: 50% likes + 30% comments + 20% shares
    - Instagram: 45% likes + 35% comments + 20% saves
    - TikTok: 40% views + 30% likes + 20% comments + 10% shares
    - Generic: equal weight all numeric metrics
    """

    if platform == "reddit":
        eng = (
            0.55 * math.log1p(metrics.get("score", 0)) +
            0.40 * math.log1p(metrics.get("comments", 0)) +
            0.05 * (metrics.get("upvote_ratio", 0.5) * 10)
        )
    elif platform in ("twitter", "x"):
        eng = (
            0.55 * math.log1p(metrics.get("likes", 0)) +
            0.25 * math.log1p(metrics.get("reposts", 0)) +
            0.15 * math.log1p(metrics.get("replies", 0)) +
            0.05 * math.log1p(metrics.get("quotes", 0))
        )
    elif platform == "youtube":
        eng = (
            0.50 * math.log1p(metrics.get("views", 0)) +
            0.35 * math.log1p(metrics.get("likes", 0)) +
            0.15 * math.log1p(metrics.get("comments", 0))
        )
    elif platform == "linkedin":
        eng = (
            0.50 * math.log1p(metrics.get("likes", 0)) +
            0.30 * math.log1p(metrics.get("comments", 0)) +
            0.20 * math.log1p(metrics.get("shares", 0))
        )
    elif platform == "instagram":
        eng = (
            0.45 * math.log1p(metrics.get("likes", 0)) +
            0.35 * math.log1p(metrics.get("comments", 0)) +
            0.20 * math.log1p(metrics.get("saves", 0))
        )
    elif platform == "tiktok":
        eng = (
            0.40 * math.log1p(metrics.get("views", 0)) +
            0.30 * math.log1p(metrics.get("likes", 0)) +
            0.20 * math.log1p(metrics.get("comments", 0)) +
            0.10 * math.log1p(metrics.get("shares", 0))
        )
    else:
        # Generic: equal weight all numeric values
        values = [v for v in metrics.values() if isinstance(v, (int, float))]
        eng = sum(math.log1p(v) for v in values) / max(len(values), 1)

    # Normalize to 0-100 (log1p of 1M ≈ 14, so divide by 14 and scale)
    engagement_normalized = min(100, (eng / 14) * 100)

    # Overall: 45% relevance + 25% recency + 30% engagement
    overall = 0.45 * relevance + 0.25 * recency + 0.30 * engagement_normalized

    return EngagementScore(
        platform=platform,
        raw_metrics=metrics,
        engagement_score=round(engagement_normalized, 1),
        relevance_score=round(relevance, 1),
        recency_score=round(recency, 1),
        overall_score=round(overall, 1),
    )
