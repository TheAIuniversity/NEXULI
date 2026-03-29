"""
Content Embeddings — extract the 1152-dim and 2048-dim representations from TRIBE.

The post-transformer 1152-dim vector is a multimodal content fingerprint.
The 2048-dim bottleneck is optimised to predict brain activity.
Both are useful for content similarity, clustering, and recommendation.

Dependencies: numpy only (stdlib-compatible k-means included).

Usage
-----
    from embeddings import ContentEmbedding, content_similarity, find_similar_content

    emb_a = ContentEmbedding(fused_1152=..., bottleneck_2048=...)
    emb_b = ContentEmbedding(fused_1152=..., bottleneck_2048=...)

    sim = content_similarity(emb_a, emb_b, level="bottleneck")
    # 0.87 — very similar brain fingerprints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class ContentEmbedding:
    """Multi-level content embedding from TRIBE's internal representations.

    Per-timestep arrays have shape (n_timesteps, dim).
    Aggregated arrays (mean over time) have shape (dim,).
    """

    # Per-timestep embeddings
    fused_1152: np.ndarray        # (n_timesteps, 1152) — post-transformer fusion
    bottleneck_2048: np.ndarray   # (n_timesteps, 2048) — brain-optimised bottleneck

    # Aggregated embeddings (mean across time).
    # Computed automatically in __post_init__ if not supplied.
    fused_mean: np.ndarray = field(default=None)       # type: ignore[assignment]
    bottleneck_mean: np.ndarray = field(default=None)  # type: ignore[assignment]

    # Per-modality embeddings before fusion (optional — only if extracted)
    visual_384: Optional[np.ndarray] = None    # (n_timesteps, 384)
    audio_384: Optional[np.ndarray] = None     # (n_timesteps, 384)
    text_384: Optional[np.ndarray] = None      # (n_timesteps, 384)

    def __post_init__(self) -> None:
        if self.fused_mean is None:
            self.fused_mean = self.fused_1152.mean(axis=0)
        if self.bottleneck_mean is None:
            self.bottleneck_mean = self.bottleneck_2048.mean(axis=0)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self, include_timeseries: bool = False) -> dict:
        """Serialisable representation.

        include_timeseries: include per-TR arrays (large — off by default).
        """
        out: dict = {
            "fused_dim": self.fused_1152.shape[-1],
            "bottleneck_dim": self.bottleneck_2048.shape[-1],
            "n_timesteps": self.fused_1152.shape[0],
            "fused_mean": self.fused_mean.tolist(),
            "bottleneck_mean": self.bottleneck_mean.tolist(),
        }
        if include_timeseries:
            out["fused_1152"] = self.fused_1152.tolist()
            out["bottleneck_2048"] = self.bottleneck_2048.tolist()
        return out

    def save(self, path: str) -> None:
        """Save embedding to a numpy .npz file."""
        arrays: dict[str, np.ndarray] = {
            "fused_1152": self.fused_1152,
            "bottleneck_2048": self.bottleneck_2048,
            "fused_mean": self.fused_mean,
            "bottleneck_mean": self.bottleneck_mean,
        }
        if self.visual_384 is not None:
            arrays["visual_384"] = self.visual_384
        if self.audio_384 is not None:
            arrays["audio_384"] = self.audio_384
        if self.text_384 is not None:
            arrays["text_384"] = self.text_384
        np.savez_compressed(path, **arrays)

    @classmethod
    def load(cls, path: str) -> "ContentEmbedding":
        """Load embedding from a .npz file saved with save()."""
        data = np.load(path, allow_pickle=False)
        return cls(
            fused_1152=data["fused_1152"],
            bottleneck_2048=data["bottleneck_2048"],
            fused_mean=data.get("fused_mean"),         # type: ignore[arg-type]
            bottleneck_mean=data.get("bottleneck_mean"),  # type: ignore[arg-type]
            visual_384=data["visual_384"] if "visual_384" in data else None,
            audio_384=data["audio_384"] if "audio_384" in data else None,
            text_384=data["text_384"] if "text_384" in data else None,
        )


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D embedding vectors.

    Returns value in [-1, 1].  Returns 0.0 if either vector has zero norm.
    """
    if a.ndim != 1 or b.ndim != 1:
        raise ValueError("cosine_similarity expects 1-D arrays")
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a < 1e-8 or norm_b < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def content_similarity(
    emb_a: ContentEmbedding,
    emb_b: ContentEmbedding,
    level: str = "bottleneck",
) -> float:
    """Compare two content pieces by their TRIBE embeddings.

    Parameters
    ----------
    level:
        "fused"      → compare 1152-dim post-transformer vectors
        "bottleneck" → compare 2048-dim brain-optimised vectors (recommended)

    Returns cosine similarity in [-1, 1].
    """
    if level == "fused":
        return cosine_similarity(emb_a.fused_mean, emb_b.fused_mean)
    if level == "bottleneck":
        return cosine_similarity(emb_a.bottleneck_mean, emb_b.bottleneck_mean)
    raise ValueError(f"Unknown level: {level!r}. Use 'fused' or 'bottleneck'.")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def find_similar_content(
    query_embedding: ContentEmbedding,
    database: list[tuple[str, ContentEmbedding]],
    top_k: int = 5,
    level: str = "bottleneck",
) -> list[tuple[str, float]]:
    """Find the most similar content in a database by brain fingerprint.

    Parameters
    ----------
    query_embedding:
        The content you want to match against.
    database:
        List of (content_id, embedding) pairs to search.
    top_k:
        Number of results to return.
    level:
        Embedding level to compare ("fused" or "bottleneck").

    Returns
    -------
    List of (content_id, similarity_score) sorted by descending similarity.
    """
    if not database:
        return []

    results: list[tuple[str, float]] = [
        (content_id, content_similarity(query_embedding, emb, level=level))
        for content_id, emb in database
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def cluster_content(
    embeddings: list[tuple[str, ContentEmbedding]],
    n_clusters: int = 5,
    level: str = "bottleneck",
    max_iterations: int = 100,
    random_seed: int = 42,
) -> dict[int, list[str]]:
    """Cluster content by brain response similarity using k-means.

    Pure-numpy implementation — no sklearn dependency.

    Parameters
    ----------
    embeddings:
        List of (content_id, embedding) pairs.
    n_clusters:
        Number of clusters.  Reduced to len(embeddings) if fewer items exist.
    level:
        "fused" or "bottleneck".
    max_iterations:
        Maximum k-means iterations.
    random_seed:
        RNG seed for reproducible initialisation.

    Returns
    -------
    {cluster_id: [content_ids]}
    """
    if not embeddings:
        return {}

    n = len(embeddings)
    k = min(n_clusters, n)

    # Build matrix
    if level == "fused":
        vectors = np.array([emb.fused_mean for _, emb in embeddings], dtype=float)
    else:
        vectors = np.array([emb.bottleneck_mean for _, emb in embeddings], dtype=float)

    ids = [cid for cid, _ in embeddings]

    if k == 1:
        return {0: ids}

    rng = np.random.RandomState(random_seed)
    center_indices = rng.choice(n, k, replace=False)
    centers = vectors[center_indices].copy()

    labels = np.zeros(n, dtype=int)

    for iteration in range(max_iterations):
        # Assignment step: find nearest center for each vector
        # Compute squared Euclidean distances via broadcasting
        diffs = vectors[:, np.newaxis, :] - centers[np.newaxis, :, :]  # (n, k, dim)
        dists_sq = (diffs ** 2).sum(axis=2)                             # (n, k)
        new_labels = dists_sq.argmin(axis=1)

        # Update step: recompute centers
        new_centers = np.zeros_like(centers)
        for j in range(k):
            mask = new_labels == j
            if mask.any():
                new_centers[j] = vectors[mask].mean(axis=0)
            else:
                # Empty cluster — reinitialise to a random point
                new_centers[j] = vectors[rng.randint(n)]

        if np.array_equal(new_labels, labels) and np.allclose(centers, new_centers, atol=1e-6):
            break

        labels = new_labels
        centers = new_centers

    clusters: dict[int, list[str]] = {}
    for i, label in enumerate(labels):
        clusters.setdefault(int(label), []).append(ids[i])

    return clusters
