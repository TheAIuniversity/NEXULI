"""
Near-Duplicate Content Detection.
Pattern stolen from goviralbitch's trigram Jaccard similarity.
"""

from typing import List, Tuple, Set


def _trigrams(text: str) -> Set[str]:
    """Extract character trigrams from text."""
    text = text.lower().strip()
    if len(text) < 3:
        return {text}
    return {text[i:i + 3] for i in range(len(text) - 2)}


def jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two texts using character trigrams."""
    tri_a = _trigrams(a)
    tri_b = _trigrams(b)
    if not tri_a or not tri_b:
        return 0.0
    intersection = len(tri_a & tri_b)
    union = len(tri_a | tri_b)
    return intersection / union if union > 0 else 0.0


def deduplicate_content(
    items: List[dict],
    text_key: str = "content",
    threshold: float = 0.7,
    score_key: str = "score",
) -> List[dict]:
    """Remove near-duplicate items, keeping the highest-scored one from each cluster.

    items: list of dicts, each containing at least text_key
    threshold: Jaccard similarity threshold (0.7 = 70% similar = duplicate)
    score_key: which field to use for picking the best from duplicates

    Returns deduplicated list.
    """
    if not items:
        return []

    # Pre-compute trigrams
    trigrams = [_trigrams(item.get(text_key, "")) for item in items]

    # Find duplicate pairs
    to_remove: set = set()
    for i in range(len(items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(items)):
            if j in to_remove:
                continue

            # Quick length check — very different lengths can't be duplicates
            tri_i, tri_j = trigrams[i], trigrams[j]
            if len(tri_i) > 0 and len(tri_j) > 0:
                ratio = min(len(tri_i), len(tri_j)) / max(len(tri_i), len(tri_j))
                if ratio < threshold:
                    continue

            similarity = (
                len(tri_i & tri_j) / len(tri_i | tri_j)
                if (tri_i | tri_j)
                else 0
            )

            if similarity >= threshold:
                # Keep the higher-scored one
                score_i = items[i].get(score_key, 0) or 0
                score_j = items[j].get(score_key, 0) or 0
                if score_i >= score_j:
                    to_remove.add(j)
                else:
                    to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]
