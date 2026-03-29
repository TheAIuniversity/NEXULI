"""
Autonomous Loop — the infinite engineering loop adapted for TRIBE marketing.

Pattern stolen from 1st agentic system's /go command:
check goal → get task → plan → execute → validate → loop

Applied to TRIBE:
score content → find weak spots → optimize → re-score → loop until target hit
"""

import time
import asyncio
import logging
from typing import Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LoopState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class LoopTask:
    """A single task in the autonomous loop."""
    id: str
    name: str
    task_type: str  # "score", "optimize", "research", "scout", "learn"
    priority: int   # 1 (highest) - 5 (lowest)
    model: str      # "haiku", "sonnet", "opus" — for model routing
    goal: str       # what success looks like
    steps: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    attempts: int = 0
    max_attempts: int = 5
    result: Optional[dict] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class LoopCycle:
    """One complete cycle of the loop."""
    cycle_number: int
    started_at: float
    completed_at: Optional[float] = None
    tasks_executed: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    goal_complete: bool = False


class AutonomousLoop:
    """The infinite loop that drives TRIBE agents.

    Pattern from /go:
    1. Check goal — are we done?
    2. Get task — from queue or generate via strategist
    3. Execute — run the task (score, optimize, scout, etc.)
    4. Validate — did it work?
    5. Loop — back to 1

    Applied to TRIBE marketing:
    - Goal: hit target score for a campaign / score all pending content / monitor competitors
    - Tasks: score content, optimize weak spots, research competitors, learn from results
    - Validation: re-score after optimization to check improvement
    """

    def __init__(self):
        self.state = LoopState.IDLE
        self.task_queue: List[LoopTask] = []
        self.current_task: Optional[LoopTask] = None
        self.cycle_history: List[LoopCycle] = []
        self.current_cycle: Optional[LoopCycle] = None
        self._cycle_count = 0
        self._running = False
        self._on_task_execute: Optional[Callable] = None
        self._on_cycle_complete: Optional[Callable] = None
        self._goal_checker: Optional[Callable] = None

    def configure(
        self,
        on_task_execute: Callable = None,
        on_cycle_complete: Callable = None,
        goal_checker: Callable = None,
    ):
        """Configure callbacks for the loop.

        on_task_execute: async (task: LoopTask) -> dict  — runs the actual task
        on_cycle_complete: async (cycle: LoopCycle) -> None  — called after each cycle
        goal_checker: async () -> bool  — returns True when goal is complete
        """
        self._on_task_execute = on_task_execute
        self._on_cycle_complete = on_cycle_complete
        self._goal_checker = goal_checker

    def add_task(self, task: LoopTask):
        """Add a task to the queue, sorted by priority."""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority)

    def add_tasks(self, tasks: List[LoopTask]):
        """Add multiple tasks."""
        for t in tasks:
            self.add_task(t)

    def _get_next_task(self) -> Optional[LoopTask]:
        """Get the highest priority pending task."""
        for task in self.task_queue:
            if task.status == "pending":
                return task
        return None

    async def run(self, max_cycles: int = 100):
        """Run the autonomous loop.

        Loops until:
        - Goal is complete (goal_checker returns True)
        - max_cycles reached
        - Manually stopped
        - All tasks completed and no new ones generated
        """
        if self.state == LoopState.RUNNING:
            logger.warning("Loop already running")
            return

        self._running = True
        self.state = LoopState.RUNNING
        logger.info(f"Autonomous loop started. {len(self.task_queue)} tasks in queue.")

        try:
            while self._running and self._cycle_count < max_cycles:
                # Step 0: Check goal
                if self._goal_checker:
                    if await self._goal_checker():
                        self.state = LoopState.COMPLETED
                        logger.info("GOAL COMPLETE. Loop stopping.")
                        break

                # Start new cycle
                self._cycle_count += 1
                self.current_cycle = LoopCycle(
                    cycle_number=self._cycle_count,
                    started_at=time.time(),
                )

                # Step 1: Get task
                task = self._get_next_task()
                if task is None:
                    # No tasks — check if we should generate more
                    logger.info("No pending tasks. Loop idle.")
                    self.state = LoopState.IDLE
                    break

                # Step 2: Execute task
                self.current_task = task
                task.status = "running"
                task.attempts += 1

                logger.info(
                    f"Cycle {self._cycle_count}: Executing [{task.task_type}] "
                    f"{task.name} (attempt {task.attempts}/{task.max_attempts})"
                )

                try:
                    if self._on_task_execute:
                        result = await self._on_task_execute(task)
                        task.result = result
                        task.status = "completed"
                        self.current_cycle.tasks_succeeded += 1
                        logger.info(f"Task completed: {task.name}")
                    else:
                        task.status = "completed"
                        logger.warning("No task executor configured")
                except Exception as e:
                    task.status = "failed" if task.attempts >= task.max_attempts else "pending"
                    self.current_cycle.tasks_failed += 1
                    logger.error(f"Task failed: {task.name} — {e}")

                    if task.status == "pending":
                        logger.info(f"Will retry ({task.attempts}/{task.max_attempts})")

                self.current_cycle.tasks_executed += 1
                self.current_task = None

                # Step 3: Complete cycle
                self.current_cycle.completed_at = time.time()
                self.cycle_history.append(self.current_cycle)

                if self._on_cycle_complete:
                    await self._on_cycle_complete(self.current_cycle)

                # Brief pause between cycles to prevent CPU spinning
                await asyncio.sleep(0.1)

            if self._cycle_count >= max_cycles:
                logger.info(f"Max cycles ({max_cycles}) reached. Loop stopping.")
                self.state = LoopState.COMPLETED

        except Exception as e:
            self.state = LoopState.ERROR
            logger.error(f"Loop error: {e}")
            raise
        finally:
            self._running = False

    def stop(self):
        """Stop the loop after current task completes."""
        self._running = False
        self.state = LoopState.IDLE
        logger.info("Loop stop requested")

    def pause(self):
        """Pause the loop."""
        self.state = LoopState.PAUSED
        self._running = False
        logger.info("Loop paused")

    def get_status(self) -> dict:
        """Get current loop status."""
        pending = sum(1 for t in self.task_queue if t.status == "pending")
        completed = sum(1 for t in self.task_queue if t.status == "completed")
        failed = sum(1 for t in self.task_queue if t.status == "failed")

        return {
            "state": self.state.value,
            "cycle_count": self._cycle_count,
            "tasks_pending": pending,
            "tasks_completed": completed,
            "tasks_failed": failed,
            "current_task": self.current_task.name if self.current_task else None,
            "queue_size": len(self.task_queue),
        }
