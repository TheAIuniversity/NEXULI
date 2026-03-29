"""
Goal Tracker — single source of truth for campaign/system goals.

Pattern from 1st agentic system's goal.md:
- Objective, success criteria, progress tracking
- GOAL_COMPLETE when all criteria met
"""

import time
import json
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field, asdict
from config import settings

logger = logging.getLogger(__name__)

GOALS_PATH = settings.db_path.parent / "goals.json"


@dataclass
class Goal:
    """A trackable goal with success criteria."""
    id: str
    objective: str
    criteria: List[dict] = field(default_factory=list)  # [{description, met: bool}]
    campaign_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    @property
    def is_complete(self) -> bool:
        return all(c.get("met", False) for c in self.criteria) if self.criteria else False

    @property
    def progress_pct(self) -> float:
        if not self.criteria:
            return 0.0
        met = sum(1 for c in self.criteria if c.get("met", False))
        return round(met / len(self.criteria) * 100, 1)

    def to_dict(self):
        d = asdict(self)
        d["is_complete"] = self.is_complete
        d["progress_pct"] = self.progress_pct
        return d


class GoalTracker:
    """Manages goals and checks completion."""

    def __init__(self):
        self.goals: dict[str, Goal] = {}
        self._load()

    def _load(self):
        if GOALS_PATH.exists():
            try:
                data = json.loads(GOALS_PATH.read_text())
                for gid, gdata in data.items():
                    self.goals[gid] = Goal(**gdata)
            except Exception:
                pass

    def _save(self):
        GOALS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {gid: asdict(g) for gid, g in self.goals.items()}
        GOALS_PATH.write_text(json.dumps(data, indent=2))

    def create(
        self,
        goal_id: str,
        objective: str,
        criteria: List[str],
        campaign_id: str = None,
    ) -> Goal:
        """Create a new goal."""
        goal = Goal(
            id=goal_id,
            objective=objective,
            criteria=[{"description": c, "met": False} for c in criteria],
            campaign_id=campaign_id,
        )
        self.goals[goal_id] = goal
        self._save()
        logger.info(f"Goal created: {objective} ({len(criteria)} criteria)")
        return goal

    def check_criterion(self, goal_id: str, criterion_index: int, met: bool = True):
        """Mark a criterion as met/unmet."""
        goal = self.goals.get(goal_id)
        if goal and 0 <= criterion_index < len(goal.criteria):
            goal.criteria[criterion_index]["met"] = met
            if goal.is_complete and not goal.completed_at:
                goal.completed_at = time.time()
                logger.info(f"GOAL COMPLETE: {goal.objective}")
            self._save()

    def is_complete(self, goal_id: str) -> bool:
        """Check if a goal is complete."""
        goal = self.goals.get(goal_id)
        return goal.is_complete if goal else False

    def get_active_goals(self) -> List[dict]:
        """Get all incomplete goals."""
        return [g.to_dict() for g in self.goals.values() if not g.is_complete]

    def get_all(self) -> dict:
        return {gid: g.to_dict() for gid, g in self.goals.items()}
