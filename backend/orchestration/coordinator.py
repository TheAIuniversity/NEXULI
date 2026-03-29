"""
Campaign Coordinator — manages content campaigns through the full lifecycle.

Pattern from 1st agentic system's coordinator:
State machine: IDLE → PICKING → PROCESSING → BLOCKED → REVIEWING → COMPLETED
Hub-based: ideas → ongoing → finished with human review gates
"""

import time
import logging
from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


class CampaignState(Enum):
    DRAFT = "draft"           # Created, not started
    SCORING = "scoring"       # Running through TRIBE
    OPTIMIZING = "optimizing" # Applying fixes
    RESCORING = "rescoring"   # Re-scoring after optimization
    REVIEW = "review"         # Waiting for human review
    APPROVED = "approved"     # Human approved, ready to deploy
    DEPLOYED = "deployed"     # Live
    COMPLETED = "completed"   # Done, results tracked


@dataclass
class Campaign:
    """A content campaign moving through the pipeline."""
    id: str
    name: str
    content_files: List[str] = field(default_factory=list)
    target_score: int = 75
    state: CampaignState = CampaignState.DRAFT

    # Scoring results
    scores: Dict[str, dict] = field(default_factory=dict)       # filename -> score result
    recommendations: Dict[str, list] = field(default_factory=dict)  # filename -> recs

    # Tracking
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    optimization_rounds: int = 0
    max_optimization_rounds: int = 3

    # Review
    reviewer_notes: str = ""
    approved_at: Optional[float] = None

    def to_dict(self):
        d = asdict(self)
        d["state"] = self.state.value
        return d


class Coordinator:
    """Manages campaigns through the full lifecycle.

    The state machine:
    DRAFT → SCORING → OPTIMIZING → RESCORING → REVIEW → APPROVED → DEPLOYED → COMPLETED
                 ^                      |
                 └──────────────────────┘  (loop if still below target)

    Human review gate between RESCORING and APPROVED.
    """

    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self._active_campaign_id: Optional[str] = None

    def create_campaign(
        self,
        campaign_id: str,
        name: str,
        content_files: List[str],
        target_score: int = 75,
    ) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign(
            id=campaign_id,
            name=name,
            content_files=content_files,
            target_score=target_score,
        )
        self.campaigns[campaign_id] = campaign
        logger.info(
            f"Campaign created: {name} ({len(content_files)} files, target: {target_score})"
        )
        return campaign

    def advance(self, campaign_id: str) -> CampaignState:
        """Advance campaign to next state based on current results.

        This is the coordinator's main decision logic.
        Returns the new state.
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")

        campaign.updated_at = time.time()

        if campaign.state == CampaignState.DRAFT:
            # Start scoring
            campaign.state = CampaignState.SCORING
            logger.info(f"Campaign {campaign.name}: DRAFT → SCORING")

        elif campaign.state == CampaignState.SCORING:
            # Check if all content is scored
            all_scored = all(f in campaign.scores for f in campaign.content_files)
            if all_scored:
                # Check if any below target
                below_target = any(
                    s.get("overall_score", 0) < campaign.target_score
                    for s in campaign.scores.values()
                )
                if below_target and campaign.optimization_rounds < campaign.max_optimization_rounds:
                    campaign.state = CampaignState.OPTIMIZING
                    logger.info(f"Campaign {campaign.name}: SCORING → OPTIMIZING (below target)")
                else:
                    campaign.state = CampaignState.REVIEW
                    logger.info(f"Campaign {campaign.name}: SCORING → REVIEW")

        elif campaign.state == CampaignState.OPTIMIZING:
            # After optimization, re-score
            campaign.optimization_rounds += 1
            campaign.state = CampaignState.RESCORING
            logger.info(
                f"Campaign {campaign.name}: OPTIMIZING → RESCORING "
                f"(round {campaign.optimization_rounds})"
            )

        elif campaign.state == CampaignState.RESCORING:
            # After re-scoring, check if target hit
            all_above = all(
                s.get("overall_score", 0) >= campaign.target_score
                for s in campaign.scores.values()
            )
            if all_above or campaign.optimization_rounds >= campaign.max_optimization_rounds:
                campaign.state = CampaignState.REVIEW
                logger.info(f"Campaign {campaign.name}: RESCORING → REVIEW")
            else:
                campaign.state = CampaignState.OPTIMIZING
                logger.info(
                    f"Campaign {campaign.name}: RESCORING → OPTIMIZING (still below target)"
                )

        elif campaign.state == CampaignState.REVIEW:
            # Human must call approve() or reject()
            pass

        elif campaign.state == CampaignState.APPROVED:
            campaign.state = CampaignState.DEPLOYED
            logger.info(f"Campaign {campaign.name}: APPROVED → DEPLOYED")

        elif campaign.state == CampaignState.DEPLOYED:
            campaign.state = CampaignState.COMPLETED
            logger.info(f"Campaign {campaign.name}: DEPLOYED → COMPLETED")

        return campaign.state

    def approve(self, campaign_id: str, notes: str = "") -> Campaign:
        """Human approves a campaign in REVIEW state."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        if campaign.state != CampaignState.REVIEW:
            raise ValueError(f"Campaign not in REVIEW state: {campaign.state.value}")

        campaign.state = CampaignState.APPROVED
        campaign.reviewer_notes = notes
        campaign.approved_at = time.time()
        campaign.updated_at = time.time()
        logger.info(f"Campaign {campaign.name}: REVIEW → APPROVED")
        return campaign

    def reject(self, campaign_id: str, notes: str = "") -> Campaign:
        """Human rejects — send back to optimization."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")

        campaign.state = CampaignState.OPTIMIZING
        campaign.reviewer_notes = notes
        campaign.optimization_rounds = 0  # Reset rounds
        campaign.updated_at = time.time()
        logger.info(f"Campaign {campaign.name}: REJECTED → OPTIMIZING")
        return campaign

    def add_score(self, campaign_id: str, filename: str, score_result: dict):
        """Add a scoring result for a content file."""
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            campaign.scores[filename] = score_result
            campaign.updated_at = time.time()

    def add_recommendations(self, campaign_id: str, filename: str, recs: list):
        """Add optimization recommendations for a content file."""
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            campaign.recommendations[filename] = recs
            campaign.updated_at = time.time()

    def get_status(self) -> dict:
        """Get status of all campaigns."""
        return {
            "campaigns": {
                cid: c.to_dict() for cid, c in self.campaigns.items()
            },
            "active": self._active_campaign_id,
            "counts": {
                state.value: sum(1 for c in self.campaigns.values() if c.state == state)
                for state in CampaignState
            },
        }

    def get_pipeline(self) -> dict:
        """Get hub-style pipeline view.

        Pattern from coordinator.md:
        ideas (draft) → ongoing (scoring/optimizing) → finished (review/approved)
        """
        return {
            "ideas": [
                c.to_dict() for c in self.campaigns.values()
                if c.state == CampaignState.DRAFT
            ],
            "ongoing": [
                c.to_dict() for c in self.campaigns.values()
                if c.state in (
                    CampaignState.SCORING,
                    CampaignState.OPTIMIZING,
                    CampaignState.RESCORING,
                )
            ],
            "review": [
                c.to_dict() for c in self.campaigns.values()
                if c.state == CampaignState.REVIEW
            ],
            "finished": [
                c.to_dict() for c in self.campaigns.values()
                if c.state in (
                    CampaignState.APPROVED,
                    CampaignState.DEPLOYED,
                    CampaignState.COMPLETED,
                )
            ],
        }
