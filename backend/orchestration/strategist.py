"""
Strategist — generates tasks based on current state and goals.

Pattern from 1st agentic system's strategist.md:
read goal → assess progress → identify gaps → generate tasks
"""

import time
import logging
from typing import List
from orchestration.loop import LoopTask

logger = logging.getLogger(__name__)


class Strategist:
    """Generates tasks for the autonomous loop based on current system state.

    Looks at:
    - What content needs scoring (pending uploads)
    - What scored content needs optimization (low scores)
    - What competitors need scanning (stale data)
    - What patterns need discovering (enough new data?)
    - What calibration needs updating (new real-world results?)
    """

    def generate_tasks(self, system_state: dict) -> List[LoopTask]:
        """Generate 1-5 tasks based on current gaps.

        system_state should contain:
        - pending_content: list of files awaiting scoring
        - low_scoring_content: list of scored content below target
        - stale_competitors: competitors not scanned recently
        - scores_since_last_learn: count of new scores since last pattern analysis
        - brain_content_scored: total items in brain
        - active_campaigns: campaigns with goals
        """
        tasks = []
        task_id = 0

        # Priority 1: Score pending content
        pending = system_state.get("pending_content", [])
        for item in pending[:3]:  # Max 3 scoring tasks at once
            task_id += 1
            tasks.append(LoopTask(
                id=f"score-{task_id}-{int(time.time())}",
                name=f"Score: {item.get('filename', 'unknown')}",
                task_type="score",
                priority=1,
                model="sonnet",  # Scoring needs medium complexity
                goal="Score content through TRIBE and store results",
                steps=[
                    f"Load file: {item.get('path', '')}",
                    "Run TRIBE prediction",
                    "Convert to marketing scores",
                    "Store in database",
                    "Update brain benchmarks",
                    "Add episode to knowledge graph",
                ],
            ))

        # Priority 2: Optimize low-scoring content
        low_scores = system_state.get("low_scoring_content", [])
        for item in low_scores[:2]:  # Max 2 optimization tasks
            task_id += 1
            tasks.append(LoopTask(
                id=f"optimize-{task_id}-{int(time.time())}",
                name=f"Optimize: {item.get('filename', 'unknown')} (score: {item.get('score', '?')})",
                task_type="optimize",
                priority=2,
                model="sonnet",
                goal="Generate optimization recommendations to improve score above target",
                steps=[
                    f"Load score result for {item.get('filename', '')}",
                    "Analyze weak moments",
                    "Generate fix recommendations",
                    "Store recommendations",
                    "Log to knowledge graph",
                ],
            ))

        # Priority 3: Scout stale competitors
        stale = system_state.get("stale_competitors", [])
        for comp in stale[:2]:
            task_id += 1
            tasks.append(LoopTask(
                id=f"scout-{task_id}-{int(time.time())}",
                name=f"Scout: {comp.get('name', 'unknown')}",
                task_type="scout",
                priority=3,
                model="haiku",  # Scraping is simple
                goal="Scan competitor pages and update profile",
                steps=[
                    f"Scrape {comp.get('url', '')}",
                    "Extract tech stack and trackers",
                    "Extract CTA patterns",
                    "Update competitor profile in brain",
                    "Add episode to knowledge graph",
                ],
            ))

        # Priority 4: Learn patterns (if enough new data)
        scores_since_learn = system_state.get("scores_since_last_learn", 0)
        if scores_since_learn >= 5:
            task_id += 1
            tasks.append(LoopTask(
                id=f"learn-{task_id}-{int(time.time())}",
                name="Learn: Analyze patterns from recent scores",
                task_type="learn",
                priority=4,
                model="haiku",  # Pattern analysis is straightforward
                goal="Discover new patterns from scored content",
                steps=[
                    "Load all recent scores",
                    "Analyze hook score correlations",
                    "Analyze modality patterns",
                    "Identify new patterns",
                    "Update brain with findings",
                    "Write patterns to knowledge graph",
                ],
            ))

        # Priority 5: Calibrate (if enough data with real results)
        total_scored = system_state.get("brain_content_scored", 0)
        if total_scored >= 20 and total_scored % 10 == 0:  # Every 10 scores
            task_id += 1
            tasks.append(LoopTask(
                id=f"calibrate-{task_id}-{int(time.time())}",
                name="Calibrate: Update brain weights from real performance",
                task_type="calibrate",
                priority=5,
                model="haiku",
                goal="Improve correlation between TRIBE predictions and real outcomes",
                steps=[
                    "Load paired data (TRIBE scores + real performance)",
                    "Calculate correlation per brain region",
                    "Adjust learning weights",
                    "Update brain",
                    "Log calibration to knowledge graph",
                ],
            ))

        logger.info(f"Strategist generated {len(tasks)} tasks from current state")
        return tasks

    def assess_state(self, db_conn, brain) -> dict:
        """Build the system state dict from current data.

        This is the 'assess progress' step from strategist.md.
        """
        from storage.db import get_scores, get_agent_logs

        scores = get_scores(db_conn, limit=100)
        recent_logs = get_agent_logs(db_conn, agent="learner", limit=1)

        # Find low-scoring content (below 60)
        low_scoring = [
            {"filename": s["filename"], "score": s["overall_score"]}
            for s in scores
            if s.get("overall_score") and s["overall_score"] < 60
        ]

        # Count scores since last learning run
        last_learn_time = recent_logs[0]["created_at"] if recent_logs else 0
        scores_since_learn = sum(
            1 for s in scores
            if s.get("created_at", 0) > last_learn_time
        )

        # Query for pending content: scores added in the last 5 minutes that
        # haven't yet been optimised (no optimizer log entry referencing them).
        pending_window = time.time() - 300  # 5 minutes
        recent_scores = [s for s in scores if s.get("created_at", 0) > pending_window]
        optimized_logs = get_agent_logs(db_conn, agent="optimizer", limit=50)
        optimized_filenames = {
            log.get("detail", "").split(":")[0].strip()
            for log in optimized_logs
        }
        pending_content = [
            {"filename": s["filename"], "path": ""}
            for s in recent_scores
            if s["filename"] not in optimized_filenames
        ]

        # Query for stale competitors: active competitors not scanned for >24 h.
        stale_threshold = time.time() - 86400  # 24 hours
        try:
            competitor_rows = db_conn.execute(
                """SELECT name, url, last_scanned
                   FROM competitors
                   WHERE status = 'active'
                     AND (last_scanned IS NULL OR last_scanned < ?)""",
                (stale_threshold,),
            ).fetchall()
            stale_competitors = [dict(r) for r in competitor_rows]
        except Exception:
            stale_competitors = []

        return {
            "pending_content": pending_content,
            "low_scoring_content": low_scoring,
            "stale_competitors": stale_competitors,
            "scores_since_last_learn": scores_since_learn,
            "brain_content_scored": brain.data["benchmarks"]["content_scored"],
            "total_scores": len(scores),
        }
