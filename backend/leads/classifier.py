"""
Lead Classifier — classifies leads by brain type based on content consumption + TRIBE brain maps.

Flow:
1. Lead visits pages / watches videos on your site
2. Look up each page's pre-computed TRIBE brain profile
3. Weight by engagement (watch time, scroll depth, clicks)
4. Compute lead's brain-type fingerprint
5. Classify into: Decision Maker, Emotional Connector, Visual Scanner, Audio Processor
6. Assign recommended actions
"""

import time
import logging
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from .content_map import ContentBrainMap, PageBrainProfile

logger = logging.getLogger(__name__)


class BrainType(Enum):
    DECISION_MAKER = "decision_maker"
    EMOTIONAL_CONNECTOR = "emotional_connector"
    VISUAL_SCANNER = "visual_scanner"
    AUDIO_PROCESSOR = "audio_processor"
    RESEARCHER = "researcher"
    UNKNOWN = "unknown"


BRAIN_TYPE_INFO = {
    BrainType.DECISION_MAKER: {
        "display": "Decision Maker",
        "emoji": "🧠",
        "description": "Consumes decision-heavy content (pricing, comparisons, CTAs). Ready to buy.",
        "dominant_regions": ["decision", "reward", "action"],
        "recommended_content": "Case studies with ROI, pricing comparisons, direct CTA",
        "sales_readiness": "HIGH",
        "best_channel": "Direct email + sales call",
        "urgency": "Contact within 24 hours",
    },
    BrainType.EMOTIONAL_CONNECTOR: {
        "display": "Emotional Connector",
        "emoji": "❤️",
        "description": "Consumes emotionally resonant content (testimonials, stories, community). Needs trust.",
        "dominant_regions": ["emotion", "social", "memory"],
        "recommended_content": "Testimonials, personal stories, community access",
        "sales_readiness": "MEDIUM",
        "best_channel": "Warm email sequence + community invite",
        "urgency": "Nurture over 1-2 weeks",
    },
    BrainType.VISUAL_SCANNER: {
        "display": "Visual Scanner",
        "emoji": "👁️",
        "description": "Consumes visual content quickly (short videos, demos, screenshots). Decides fast.",
        "dominant_regions": ["visual", "face", "attention"],
        "recommended_content": "Demo videos, product screenshots, visual case studies",
        "sales_readiness": "MEDIUM-HIGH",
        "best_channel": "Retargeting with video ads + visual email",
        "urgency": "Re-engage within 48 hours with visual content",
    },
    BrainType.AUDIO_PROCESSOR: {
        "display": "Audio Processor",
        "emoji": "🎧",
        "description": "Consumes audio/language-heavy content (webinars, podcasts, long reads). Wants depth.",
        "dominant_regions": ["auditory", "language"],
        "recommended_content": "Podcast links, webinar invites, detailed guides",
        "sales_readiness": "MEDIUM",
        "best_channel": "Educational email sequence + podcast/webinar",
        "urgency": "Engage with educational content over 2-4 weeks",
    },
    BrainType.RESEARCHER: {
        "display": "Researcher",
        "emoji": "🔬",
        "description": "Consumes many pages across all types. Thorough evaluator. Needs comprehensive info.",
        "dominant_regions": ["language", "decision", "memory"],
        "recommended_content": "Documentation, comparisons, detailed specs, free trial",
        "sales_readiness": "MEDIUM-HIGH",
        "best_channel": "Drip campaign with progressive depth",
        "urgency": "Don't rush — provide exhaustive information",
    },
    BrainType.UNKNOWN: {
        "display": "Unclassified",
        "emoji": "❓",
        "description": "Not enough content consumption data to classify.",
        "dominant_regions": [],
        "recommended_content": "General awareness content",
        "sales_readiness": "LOW",
        "best_channel": "Retargeting",
        "urgency": "Needs more touchpoints",
    },
}


@dataclass
class ContentInteraction:
    """One interaction: lead consumed a piece of content."""
    url: str
    timestamp: float
    duration_seconds: float = 0  # how long they engaged
    scroll_depth: float = 0  # 0-1 for pages
    clicked_cta: bool = False

    # Engagement weight (computed)
    engagement_weight: float = 1.0


@dataclass
class LeadProfile:
    """Complete TRIBE brain classification for a lead."""
    lead_id: str

    # Brain type classification
    brain_type: str  # BrainType.value
    brain_type_display: str
    brain_type_confidence: float  # 0-1

    # Brain fingerprint (weighted average across consumed content)
    brain_fingerprint: Dict[str, float] = field(default_factory=dict)

    # Top 3 dominant regions
    top_regions: List[Dict[str, float]] = field(default_factory=list)

    # Content consumption summary
    pages_visited: int = 0
    total_engagement_seconds: float = 0
    funnel_stages_touched: List[str] = field(default_factory=list)

    # Modality preference
    preferred_modality: str = ""  # "visual", "audio", "text"
    modality_scores: Dict[str, float] = field(default_factory=dict)

    # Sales signals
    sales_readiness: str = "LOW"
    recommended_content: str = ""
    recommended_channel: str = ""
    urgency: str = ""

    # Scoring
    tribe_lead_score: float = 0  # 0-100 based on brain engagement

    classified_at: float = 0

    def to_dict(self):
        return asdict(self)


class LeadClassifier:
    """Classifies leads into brain types based on content consumption + TRIBE brain maps."""

    def __init__(self, content_map: ContentBrainMap = None):
        self.content_map = content_map or ContentBrainMap()

    def classify(self, lead_id: str, interactions: List[ContentInteraction]) -> LeadProfile:
        """Classify a lead based on their content consumption history.

        1. Look up TRIBE brain profile for each page they visited
        2. Weight by engagement (longer view = higher weight)
        3. Compute weighted brain fingerprint
        4. Classify into brain type
        """
        if not interactions:
            return self._unknown_profile(lead_id)

        # Compute engagement weights
        for interaction in interactions:
            interaction.engagement_weight = self._compute_engagement_weight(interaction)

        # Build brain fingerprint
        region_totals: Dict[str, float] = {}
        region_counts: Dict[str, float] = {}
        modality_totals = {"visual": 0.0, "audio": 0.0, "text": 0.0}
        modality_weights = 0.0
        funnel_stages = set()
        total_engagement = 0.0
        matched_pages = 0

        for interaction in interactions:
            profile = self.content_map.get_profile(interaction.url)
            if not profile:
                continue

            matched_pages += 1
            w = interaction.engagement_weight
            total_engagement += interaction.duration_seconds

            if profile.funnel_stage:
                funnel_stages.add(profile.funnel_stage)

            # Accumulate weighted region scores
            for region, score in profile.get_region_scores().items():
                if region not in region_totals:
                    region_totals[region] = 0
                    region_counts[region] = 0
                region_totals[region] += score * w
                region_counts[region] += w

            # Accumulate modality preference
            modality_totals["visual"] += profile.visual_pct * w
            modality_totals["audio"] += profile.audio_pct * w
            modality_totals["text"] += profile.text_pct * w
            modality_weights += w

        if matched_pages == 0:
            return self._unknown_profile(lead_id)

        # Compute weighted averages
        brain_fingerprint = {}
        for region in region_totals:
            brain_fingerprint[region] = (
                region_totals[region] / region_counts[region]
                if region_counts[region] > 0
                else 0
            )

        # Modality preference
        if modality_weights > 0:
            modality_scores = {
                "visual": modality_totals["visual"] / modality_weights,
                "audio": modality_totals["audio"] / modality_weights,
                "text": modality_totals["text"] / modality_weights,
            }
        else:
            modality_scores = {"visual": 33, "audio": 33, "text": 34}

        preferred_modality = max(modality_scores, key=modality_scores.get)

        # Classify brain type
        brain_type = self._classify_brain_type(brain_fingerprint, interactions)
        info = BRAIN_TYPE_INFO[brain_type]

        # Compute confidence
        confidence = self._compute_confidence(brain_fingerprint, brain_type, matched_pages)

        # Top regions
        sorted_regions = sorted(brain_fingerprint.items(), key=lambda x: x[1], reverse=True)
        top_regions = [{"region": r, "score": round(s, 1)} for r, s in sorted_regions[:3]]

        # Tribe lead score (engagement-weighted overall brain activation)
        tribe_score = np.mean(list(brain_fingerprint.values())) if brain_fingerprint else 0
        # Boost for decision-stage behavior
        if "decision" in funnel_stages:
            tribe_score *= 1.3
        if any(i.clicked_cta for i in interactions):
            tribe_score *= 1.5
        tribe_score = min(100, tribe_score)

        return LeadProfile(
            lead_id=lead_id,
            brain_type=brain_type.value,
            brain_type_display=info["display"],
            brain_type_confidence=round(confidence, 2),
            brain_fingerprint={k: round(v, 1) for k, v in brain_fingerprint.items()},
            top_regions=top_regions,
            pages_visited=len(interactions),
            total_engagement_seconds=round(total_engagement, 1),
            funnel_stages_touched=sorted(funnel_stages),
            preferred_modality=preferred_modality,
            modality_scores={k: round(v, 1) for k, v in modality_scores.items()},
            sales_readiness=info["sales_readiness"],
            recommended_content=info["recommended_content"],
            recommended_channel=info["best_channel"],
            urgency=info["urgency"],
            tribe_lead_score=round(float(tribe_score), 1),
            classified_at=time.time(),
        )

    def _classify_brain_type(
        self,
        fingerprint: Dict[str, float],
        interactions: List[ContentInteraction],
    ) -> BrainType:
        """Determine brain type from fingerprint."""
        if not fingerprint:
            return BrainType.UNKNOWN

        # Check for researcher using a weighted signal rather than a hard count.
        # A lead needs a high page count AND diverse funnel stage coverage to be
        # classified as a Researcher.  This prevents a single binge session
        # (e.g. 8 views of the same blog post) from triggering the type.
        n_pages = len(interactions)
        unique_urls = len({i.url for i in interactions})
        # Researcher signal: 6+ distinct pages, OR 4+ pages spread across 3+
        # different funnel stages (visited_stages must be inferred from the
        # content map which we don't have here — use URL diversity as a proxy).
        researcher_score = (
            (min(n_pages, 12) / 12) * 0.5       # page count signal (caps at 12)
            + (min(unique_urls, 8) / 8) * 0.5    # URL diversity signal
        )
        if researcher_score >= 0.6:
            return BrainType.RESEARCHER

        # Score each brain type
        type_scores = {}

        for brain_type, info in BRAIN_TYPE_INFO.items():
            if brain_type == BrainType.UNKNOWN or brain_type == BrainType.RESEARCHER:
                continue
            score = 0
            for region in info["dominant_regions"]:
                score += fingerprint.get(region, 0)
            type_scores[brain_type] = score / max(len(info["dominant_regions"]), 1)

        if not type_scores:
            return BrainType.UNKNOWN

        # CTA click strongly indicates Decision Maker
        if any(i.clicked_cta for i in interactions):
            type_scores[BrainType.DECISION_MAKER] *= 1.5

        best_type = max(type_scores, key=type_scores.get)

        # Need minimum activation to classify
        if type_scores[best_type] < 30:
            return BrainType.UNKNOWN

        return best_type

    def _compute_engagement_weight(self, interaction: ContentInteraction) -> float:
        """Weight by engagement depth."""
        w = 1.0

        # Duration weight (log scale — 10s = 1, 60s = 2, 300s = 3)
        if interaction.duration_seconds > 0:
            w *= (1 + np.log1p(interaction.duration_seconds / 10))

        # Scroll depth weight
        if interaction.scroll_depth > 0.7:
            w *= 1.5
        elif interaction.scroll_depth > 0.4:
            w *= 1.2

        # CTA click = strong signal
        if interaction.clicked_cta:
            w *= 2.0

        return w

    def _compute_confidence(
        self,
        fingerprint: Dict[str, float],
        brain_type: BrainType,
        matched_pages: int,
    ) -> float:
        """Confidence based on data quality + separation between types."""
        if brain_type == BrainType.UNKNOWN:
            return 0

        # More matched pages = more confident
        page_conf = min(1.0, matched_pages / 5)

        # Higher dominant region scores = more confident
        info = BRAIN_TYPE_INFO[brain_type]
        dominant_scores = [fingerprint.get(r, 0) for r in info["dominant_regions"]]
        other_scores = [v for k, v in fingerprint.items() if k not in info["dominant_regions"]]

        if dominant_scores and other_scores:
            separation = np.mean(dominant_scores) - np.mean(other_scores)
            signal_conf = min(1.0, max(0, separation / 30))
        else:
            signal_conf = 0.3

        return page_conf * 0.4 + signal_conf * 0.6

    def _unknown_profile(self, lead_id: str) -> LeadProfile:
        info = BRAIN_TYPE_INFO[BrainType.UNKNOWN]
        return LeadProfile(
            lead_id=lead_id,
            brain_type=BrainType.UNKNOWN.value,
            brain_type_display=info["display"],
            brain_type_confidence=0,
            sales_readiness=info["sales_readiness"],
            recommended_content=info["recommended_content"],
            recommended_channel=info["best_channel"],
            urgency=info["urgency"],
            classified_at=time.time(),
        )
