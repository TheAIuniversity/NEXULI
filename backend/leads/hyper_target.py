"""
Hyper Targeter — generates specific actions per lead based on TRIBE brain classification.

Takes a LeadProfile and produces:
- Which content to send next
- Which channel to use
- What tone/angle to use
- When to send
- Priority score
"""

import time
import logging
from typing import List
from dataclasses import dataclass, asdict

from .classifier import LeadProfile, BrainType, BRAIN_TYPE_INFO

logger = logging.getLogger(__name__)


@dataclass
class TargetedAction:
    """One specific action to take for a lead."""
    action_type: str  # "send_email", "retarget_ad", "sales_call", "send_content", "invite_community"
    priority: str  # "critical", "high", "medium", "low"
    channel: str  # "email", "ads", "phone", "whatsapp", "community"

    # Content to send
    content_type: str  # "case_study", "testimonial", "demo", "pricing", "podcast", "guide"
    content_angle: str  # specific angle/topic

    # Messaging
    tone: str  # "direct", "warm", "educational", "urgent"
    subject_line_hint: str  # suggested email subject
    key_message: str  # the core message to communicate

    # Timing
    urgency: str  # "immediate", "within_24h", "within_week", "nurture"

    # Why this action
    reasoning: str  # brain-based reasoning
    brain_evidence: str  # which brain regions support this

    # Optional
    delay_hours: int = 0

    def to_dict(self):
        return asdict(self)


class HyperTargeter:
    """Generates hyper-targeted action plans per lead."""

    def generate_actions(self, profile: LeadProfile) -> List[TargetedAction]:
        """Generate prioritized action list for a lead based on brain type."""
        brain_type = BrainType(profile.brain_type)

        if brain_type == BrainType.UNKNOWN:
            return [self._generic_retarget(profile)]

        actions = []

        if brain_type == BrainType.DECISION_MAKER:
            actions = self._decision_maker_actions(profile)
        elif brain_type == BrainType.EMOTIONAL_CONNECTOR:
            actions = self._emotional_connector_actions(profile)
        elif brain_type == BrainType.VISUAL_SCANNER:
            actions = self._visual_scanner_actions(profile)
        elif brain_type == BrainType.AUDIO_PROCESSOR:
            actions = self._audio_processor_actions(profile)
        elif brain_type == BrainType.RESEARCHER:
            actions = self._researcher_actions(profile)

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda a: priority_order.get(a.priority, 9))

        return actions

    def _decision_maker_actions(self, p: LeadProfile) -> List[TargetedAction]:
        actions = []

        # Primary: Direct conversion attempt
        actions.append(TargetedAction(
            action_type="send_email",
            priority="critical",
            channel="email",
            content_type="pricing",
            content_angle="ROI comparison with specific numbers",
            tone="direct",
            subject_line_hint="Here's exactly what you'll save",
            key_message="Direct value proposition with numbers. No fluff. Clear CTA.",
            urgency="within_24h",
            delay_hours=0,
            reasoning="Decision Maker brain type — prefrontal cortex dominant. They've already evaluated options and are looking for the final push.",
            brain_evidence=f"Prefrontal (decision) avg: {p.brain_fingerprint.get('decision', 0)}, Reward processing: {p.brain_fingerprint.get('reward', 0)}",
        ))

        # Secondary: Social proof with data
        actions.append(TargetedAction(
            action_type="send_content",
            priority="high",
            channel="email",
            content_type="case_study",
            content_angle="Case study with measurable results (%, €, time saved)",
            tone="direct",
            subject_line_hint="How [similar company] achieved [specific result]",
            key_message="Proof that others like them made the decision and won.",
            urgency="within_24h",
            delay_hours=12,
            reasoning="Decision Makers need evidence, not emotion. Case studies activate the same prefrontal + reward circuits.",
            brain_evidence=f"Decision: {p.brain_fingerprint.get('decision', 0)}, Action impulse: {p.brain_fingerprint.get('action', 0)}",
        ))

        # If CTA was clicked: immediate sales contact
        if "decision" in p.funnel_stages_touched:
            actions.insert(0, TargetedAction(
                action_type="sales_call",
                priority="critical",
                channel="phone",
                content_type="pricing",
                content_angle="Direct: answer their specific questions, close",
                tone="direct",
                subject_line_hint="",
                key_message="They visited pricing — they're comparing. Call now before they choose a competitor.",
                urgency="immediate",
                delay_hours=0,
                reasoning="Visited decision-stage content with high prefrontal activation. Classic buying signal.",
                brain_evidence=f"Funnel: decision stage touched. Lead score: {p.tribe_lead_score}",
            ))

        return actions

    def _emotional_connector_actions(self, p: LeadProfile) -> List[TargetedAction]:
        return [
            TargetedAction(
                action_type="send_content",
                priority="high",
                channel="email",
                content_type="testimonial",
                content_angle="Personal transformation story from someone like them",
                tone="warm",
                subject_line_hint="How [name] went from [problem] to [result]",
                key_message="Show human transformation. Name, face, specific story. Make it personal.",
                urgency="within_24h",
                delay_hours=0,
                reasoning="Emotional Connector — default mode network dominant. They need to see themselves in someone else's story.",
                brain_evidence=f"Emotion: {p.brain_fingerprint.get('emotion', 0)}, Social: {p.brain_fingerprint.get('social', 0)}",
            ),
            TargetedAction(
                action_type="invite_community",
                priority="medium",
                channel="email",
                content_type="community",
                content_angle="Invite to community / group / call",
                tone="warm",
                subject_line_hint="Join [X] people who are doing this together",
                key_message="Belonging triggers. Community, not product. They buy the people, not the features.",
                urgency="within_week",
                delay_hours=48,
                reasoning="Default mode + social cognition = need for belonging before purchasing.",
                brain_evidence=f"Emotion: {p.brain_fingerprint.get('emotion', 0)}, Memory: {p.brain_fingerprint.get('memory', 0)}",
            ),
            TargetedAction(
                action_type="send_email",
                priority="medium",
                channel="email",
                content_type="guide",
                content_angle="Personal note from founder / team member",
                tone="warm",
                subject_line_hint="I noticed you were looking at...",
                key_message="Human connection. Not automated. Acknowledge them as a person.",
                urgency="within_week",
                delay_hours=96,
                reasoning="Emotional Connectors respond to human warmth, not features. Personalization = default mode activation.",
                brain_evidence=f"Social cognition: {p.brain_fingerprint.get('social', 0)}",
            ),
        ]

    def _visual_scanner_actions(self, p: LeadProfile) -> List[TargetedAction]:
        return [
            TargetedAction(
                action_type="retarget_ad",
                priority="high",
                channel="ads",
                content_type="demo",
                content_angle="15-second product demo video — face first, show the result",
                tone="direct",
                subject_line_hint="",
                key_message="Show, don't tell. Visual proof in under 15 seconds. Strong thumbnail.",
                urgency="within_24h",
                delay_hours=0,
                reasoning="Visual Scanner — high visual cortex + fusiform. They process images > words. Retarget with video, not text.",
                brain_evidence=f"Visual: {p.brain_fingerprint.get('visual', 0)}, Face: {p.brain_fingerprint.get('face', 0)}",
            ),
            TargetedAction(
                action_type="send_email",
                priority="medium",
                channel="email",
                content_type="demo",
                content_angle="Visual email: screenshot walkthrough, before/after, GIF",
                tone="direct",
                subject_line_hint="See what [product] looks like in action",
                key_message="Minimal text. Maximum visuals. Every email = a mini demo.",
                urgency="within_24h",
                delay_hours=24,
                reasoning="Visual Scanners skip text-heavy emails. Images and GIFs trigger visual cortex engagement.",
                brain_evidence=f"Visual: {p.brain_fingerprint.get('visual', 0)}, Attention: {p.brain_fingerprint.get('attention', 0)}",
            ),
        ]

    def _audio_processor_actions(self, p: LeadProfile) -> List[TargetedAction]:
        return [
            TargetedAction(
                action_type="send_content",
                priority="high",
                channel="email",
                content_type="podcast",
                content_angle="Relevant podcast episode or webinar recording",
                tone="educational",
                subject_line_hint="Listen: How to [solve their problem] in [timeframe]",
                key_message="Audio content they can consume while doing other things. Depth > speed.",
                urgency="within_24h",
                delay_hours=0,
                reasoning="Audio Processor — high auditory + language areas. They learn by listening, not scanning.",
                brain_evidence=f"Auditory: {p.brain_fingerprint.get('auditory', 0)}, Language: {p.brain_fingerprint.get('language', 0)}",
            ),
            TargetedAction(
                action_type="sales_call",
                priority="medium",
                channel="phone",
                content_type="guide",
                content_angle="Discovery call — let them talk, listen, explain",
                tone="educational",
                subject_line_hint="Can I explain how this works?",
                key_message="Audio processors WANT a conversation. Don't email — call. They process by discussing.",
                urgency="within_week",
                delay_hours=72,
                reasoning="High auditory + language = conversation-driven decision making.",
                brain_evidence=f"Auditory: {p.brain_fingerprint.get('auditory', 0)}, Language: {p.brain_fingerprint.get('language', 0)}",
            ),
        ]

    def _researcher_actions(self, p: LeadProfile) -> List[TargetedAction]:
        return [
            TargetedAction(
                action_type="send_content",
                priority="high",
                channel="email",
                content_type="guide",
                content_angle="Comprehensive guide / documentation link",
                tone="educational",
                subject_line_hint="The complete guide to [topic they researched]",
                key_message="Give them EVERYTHING. Researchers don't want to be sold — they want to be informed.",
                urgency="within_24h",
                delay_hours=0,
                reasoning="Researcher type — 8+ pages visited across topics. They're doing due diligence.",
                brain_evidence=f"Pages visited: {p.pages_visited}, Language: {p.brain_fingerprint.get('language', 0)}, Memory: {p.brain_fingerprint.get('memory', 0)}",
            ),
            TargetedAction(
                action_type="send_email",
                priority="medium",
                channel="email",
                content_type="case_study",
                content_angle="Comparison: your product vs alternatives (honest)",
                tone="educational",
                subject_line_hint="How [product] compares (honest breakdown)",
                key_message="They're comparing already. Give them YOUR comparison before they find someone else's.",
                urgency="within_week",
                delay_hours=48,
                reasoning="Researchers value honesty and completeness. Biased content triggers distrust.",
                brain_evidence=f"Decision: {p.brain_fingerprint.get('decision', 0)}, Funnel stages: {p.funnel_stages_touched}",
            ),
        ]

    def _generic_retarget(self, p: LeadProfile) -> TargetedAction:
        return TargetedAction(
            action_type="retarget_ad",
            priority="low",
            channel="ads",
            content_type="awareness",
            content_angle="General brand awareness ad",
            tone="warm",
            subject_line_hint="",
            key_message="Not enough data to personalize. Show general content to gather more brain signal.",
            urgency="nurture",
            delay_hours=0,
            reasoning="Unknown brain type — insufficient content consumption data. Need more touchpoints.",
            brain_evidence="No TRIBE data available for this lead.",
        )
