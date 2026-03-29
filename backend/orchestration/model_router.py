"""
Model Router — selects the best model for each task based on complexity.

Pattern from 1st agentic system's model-router.md:
Simple → haiku ($), Medium → sonnet ($$), Complex → opus ($$$)

Adapted with keyword detection from the original.
"""

import logging

logger = logging.getLogger(__name__)

SIMPLE_KEYWORDS = [
    "format", "rename", "typo", "comment", "commit", "push", "docs",
    "readme", "boilerplate", "log", "status", "list", "count", "fetch",
    "scrape", "scan", "ping", "check",
]

COMPLEX_KEYWORDS = [
    "architect", "design", "debug", "optimize", "security", "performance",
    "migrate", "scale", "strategy", "analyze pattern", "calibrate",
    "cross-reference", "entity resolution", "generate brief",
]

MEDIUM_KEYWORDS = [
    "build", "implement", "test", "review", "score", "recommend",
    "compare", "extract", "summarize", "classify",
]


def route_model(task_description: str, task_type: str = None) -> str:
    """Select the best model for a task.

    Returns: "haiku", "sonnet", or "opus"
    """
    desc_lower = task_description.lower()

    # Check task_type first (most reliable signal)
    type_routing = {
        "score": "sonnet",      # TRIBE scoring needs medium capability
        "optimize": "sonnet",   # Recommendations need understanding
        "scout": "haiku",       # Scraping is simple
        "learn": "haiku",       # Pattern matching is straightforward
        "calibrate": "sonnet",  # Weight adjustment needs care
        "research": "opus",     # Deep research needs max capability
        "creative": "opus",     # Brief generation needs creativity
    }

    if task_type and task_type in type_routing:
        model = type_routing[task_type]
        logger.debug(f"Model routed by type ({task_type}): {model}")
        return model

    # Fall back to keyword detection
    if any(kw in desc_lower for kw in COMPLEX_KEYWORDS):
        return "opus"

    if any(kw in desc_lower for kw in SIMPLE_KEYWORDS):
        return "haiku"

    # Default to sonnet (best balance)
    return "sonnet"


def estimate_cost(model: str, estimated_tokens: int) -> float:
    """Estimate cost in USD for a task.

    Prices approximate as of 2026:
    """
    # Per million tokens (input + output averaged)
    prices = {
        "haiku": 1.0,    # $1/M tokens
        "sonnet": 6.0,   # $6/M tokens
        "opus": 30.0,    # $30/M tokens
    }

    price_per_m = prices.get(model, 6.0)
    return (estimated_tokens / 1_000_000) * price_per_m
