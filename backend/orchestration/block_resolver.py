"""
Block Resolver — detects and resolves agent blocks.

Pattern from 1st agentic system's meta-skill.md:
Detect block type → route to appropriate solution

Block types:
- KNOWLEDGE: "I don't know how" → research
- CAPABILITY: "I can't access/do X" → find tool or ask user
- DATA: "I don't have the data" → fetch or ask user
- ERROR: "Something failed" → retry with different approach
- PERMISSION: "I need approval" → escalate to human
"""

import time
import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BlockType(Enum):
    KNOWLEDGE = "knowledge"     # Don't know how to do something
    CAPABILITY = "capability"   # Can't access a tool or service
    DATA = "data"               # Missing data needed for task
    ERROR = "error"             # Something technical failed
    PERMISSION = "permission"   # Need human approval
    RESOURCE = "resource"       # Need GPU, memory, etc.


@dataclass
class Block:
    """A detected block preventing task completion."""
    block_type: BlockType
    description: str
    agent: str              # which agent is blocked
    task_id: Optional[str] = None
    resolution: Optional[str] = None
    resolved: bool = False
    created_at: float = 0
    resolved_at: Optional[float] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class BlockResolver:
    """Detects and resolves blocks using decision tree from meta-skill.md."""

    def __init__(self):
        self.blocks: list[Block] = []
        self.resolution_history: list[Block] = []

    def detect(self, error: Exception, agent: str, task_id: str = None) -> Block:
        """Detect block type from an error."""
        error_str = str(error).lower()

        # Classify the block
        if any(kw in error_str for kw in ["not found", "no such file", "missing", "404"]):
            block_type = BlockType.DATA
        elif any(kw in error_str for kw in ["permission", "forbidden", "403", "unauthorized", "401"]):
            block_type = BlockType.PERMISSION
        elif any(kw in error_str for kw in ["gpu", "cuda", "memory", "oom", "out of memory"]):
            block_type = BlockType.RESOURCE
        elif any(kw in error_str for kw in ["timeout", "connection", "network", "dns"]):
            block_type = BlockType.CAPABILITY
        elif any(kw in error_str for kw in ["import", "module", "package", "install"]):
            block_type = BlockType.KNOWLEDGE
        else:
            block_type = BlockType.ERROR

        block = Block(
            block_type=block_type,
            description=str(error),
            agent=agent,
            task_id=task_id,
        )
        self.blocks.append(block)
        logger.warning(f"Block detected [{block_type.value}] in {agent}: {error}")
        return block

    def resolve(self, block: Block) -> str:
        """Generate resolution strategy for a block.

        Returns a resolution instruction string.
        """
        if block.block_type == BlockType.KNOWLEDGE:
            resolution = (
                "Research the error. Check documentation. "
                "If a package is missing, install it."
            )

        elif block.block_type == BlockType.CAPABILITY:
            resolution = (
                "Check network connectivity. If a service is down, retry after 60 seconds. "
                "If an API is unavailable, use cached data."
            )

        elif block.block_type == BlockType.DATA:
            resolution = (
                "Check if the file/data exists at the expected path. "
                "If missing, try fetching from source. "
                "If unfetchable, skip this task and log."
            )

        elif block.block_type == BlockType.ERROR:
            resolution = (
                "Retry with different parameters. "
                "If failed 3+ times, escalate to human review."
            )

        elif block.block_type == BlockType.PERMISSION:
            resolution = "This requires human approval. Add to review queue and wait."

        elif block.block_type == BlockType.RESOURCE:
            resolution = (
                "GPU/memory insufficient. Try reducing batch size. "
                "If TRIBE model can't load, ensure Mac Mini has enough RAM. "
                "Try CPU fallback."
            )

        else:
            resolution = "Unknown block type. Log and escalate to human review."

        block.resolution = resolution
        block.resolved = True
        block.resolved_at = time.time()
        self.resolution_history.append(block)

        logger.info(f"Block resolved [{block.block_type.value}]: {resolution}")
        return resolution

    def get_unresolved(self) -> list:
        """Get all unresolved blocks."""
        return [b for b in self.blocks if not b.resolved]

    def get_stats(self) -> dict:
        """Block resolution statistics."""
        total = len(self.blocks)
        resolved = len(self.resolution_history)
        by_type: dict = {}
        for b in self.blocks:
            t = b.block_type.value
            by_type[t] = by_type.get(t, 0) + 1

        return {
            "total_blocks": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "by_type": by_type,
        }
