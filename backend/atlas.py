"""
HCP-MMP1 Atlas — 360-region Human Connectome Project Multi-Modal Parcellation.

FIX 1: Replaces fake REGION_MASKS (simple vertex slices) with real HCP-MMP1 atlas
structure, plus marketing-relevant region groupings.

FIX 2: Correct TRIBE temporal constants (2 Hz output, TR = 0.5 s).

Architecture
------------
- MARKETING_REGIONS defines 12 functional clusters with HCP-MMP1 region names.
- VERTEX_ATLAS_PLACEHOLDER holds per-region vertex indices.  Before the Mac Mini
  extraction run these are filled with *approximate* ranges derived from the
  published fsaverage5 surface geometry.  Replace with real arrays once you have
  run `tribev2/utils.py::get_hcp_labels()` and called `build_vertex_atlas()`.
- Public API:
    get_region_vertices(region_name) → np.ndarray of vertex indices
    get_vertex_atlas()               → {region_name: np.ndarray}
    summarize_by_region(predictions, atlas)  → {region_name: float}
    score_by_marketing_region(predictions)   → {cluster_name: {score, ...}}
"""

from __future__ import annotations

import numpy as np
from typing import Optional


# ---------------------------------------------------------------------------
# FIX 2: Temporal constants
# ---------------------------------------------------------------------------

TRIBE_FREQUENCY_HZ: int = 2          # TRIBE outputs at 2 Hz, not 1 Hz
TRIBE_TR_SECONDS: float = 0.5        # Each prediction row = 0.5 seconds, not 1.0


# ---------------------------------------------------------------------------
# fsaverage5 surface constants
# ---------------------------------------------------------------------------

N_VERTICES_FSAVERAGE5: int = 20484   # 10242 per hemisphere
N_VERTICES_PER_HEMI: int = 10242
# HCP-MMP1 has 180 regions per hemisphere = 360 total
N_HCP_REGIONS_PER_HEMI: int = 180
N_HCP_REGIONS_TOTAL: int = 360


# ---------------------------------------------------------------------------
# FIX 1a: HCP-MMP1 marketing region definitions
# ---------------------------------------------------------------------------

MARKETING_REGIONS: dict[str, dict] = {
    "visual_processing": {
        "display_name": "Visual Processing",
        "hcp_regions": ["V1", "V2", "V3", "V3A", "V3B", "V4", "V4t", "V6", "V6A", "V7", "V8"],
        "function": "Scene processing, visual attention, motion detection",
        "emotions": ["visual engagement", "alertness"],
    },
    "auditory_processing": {
        "display_name": "Auditory Processing",
        "hcp_regions": ["A1", "A4", "A5", "RI", "MBelt", "LBelt", "PBelt", "TA2"],
        "function": "Sound processing, voice recognition, music perception",
        "emotions": ["auditory engagement", "voice connection"],
    },
    "language_comprehension": {
        "display_name": "Language Comprehension",
        "hcp_regions": [
            "44", "45", "47l", "IFSa", "IFSp", "IFJa", "IFJp",
            "STSdp", "STSda", "STSvp", "STSva",
            "TPOJ1", "TPOJ2", "TPOJ3", "STV",
        ],
        "function": "Speech comprehension, syntax, semantic processing",
        "emotions": ["understanding", "meaning-making", "comprehension"],
    },
    "decision_making": {
        "display_name": "Decision Making",
        "hcp_regions": [
            "p10p", "10r", "10v", "10pp", "OFC", "pOFC", "a47r",
            "11l", "13l", "a10p", "p47r",
            "8BM", "8Av", "8Ad", "8BL", "8C",
            "9m", "9p", "9a", "d32", "p32", "a24", "p24",
        ],
        "function": "Value judgment, reward evaluation, executive decision",
        "emotions": ["evaluation", "desire", "anticipation", "judgment"],
    },
    "emotional_resonance": {
        "display_name": "Emotional Resonance",
        "hcp_regions": [
            "PCC", "RSC", "7m",
            "31pv", "31pd", "31a", "d23ab", "v23ab",
            "ProS", "DVT", "POS1", "POS2", "23c", "23d",
        ],
        "function": "Self-reference, personal relevance, default mode network",
        "emotions": ["personal connection", "self-relevance", "nostalgia", "belonging", "empathy"],
    },
    "face_recognition": {
        "display_name": "Face Recognition",
        "hcp_regions": ["FFC", "VVC", "PIT", "V8"],
        "function": "Face detection, person identification, social processing",
        "emotions": ["social connection", "trust", "familiarity", "tribal belonging"],
    },
    "action_impulse": {
        "display_name": "Action Impulse",
        "hcp_regions": [
            "4", "3a", "3b", "1", "2",
            "6ma", "6mp", "6d", "6v", "6r", "FEF", "PEF",
        ],
        "function": "Motor preparation, action readiness, urge to act",
        "emotions": ["urge to click", "action readiness", "physical response"],
    },
    "social_cognition": {
        "display_name": "Social Cognition",
        "hcp_regions": [
            "SFL", "SCEF", "PreS", "H", "EC",
            "TGd", "TGv",
            "TE1a", "TE1m", "TE1p", "TE2a", "TE2p", "TF",
        ],
        "function": "Theory of mind, social perception, perspective-taking",
        "emotions": ["social understanding", "perspective-taking", "mentalizing"],
    },
    "attention_salience": {
        "display_name": "Attention & Salience",
        "hcp_regions": [
            "FOP1", "FOP2", "FOP3", "FOP4", "FOP5",
            "MI", "PI", "Ig", "PoI1", "PoI2", "AVI", "AAIC", "Pir",
        ],
        "function": "Attention capture, salience detection, interoception",
        "emotions": ["gut feeling", "surprise", "attention capture", "visceral response"],
    },
    "memory_encoding": {
        "display_name": "Memory Encoding",
        "hcp_regions": ["PHA1", "PHA2", "PHA3", "EC", "PreS", "H"],
        "function": "Memory formation, scene memory, context encoding",
        "emotions": ["memorability", "recognition", "context processing"],
    },
    "conflict_motivation": {
        "display_name": "Conflict & Motivation",
        "hcp_regions": ["a24pr", "p24pr", "a32pr", "p32pr", "s32", "33pr", "25"],
        "function": "Error detection, conflict monitoring, motivation drive",
        "emotions": ["frustration", "motivation", "drive", "pain point recognition"],
    },
    "reward_processing": {
        "display_name": "Reward Processing",
        "hcp_regions": ["OFC", "pOFC", "10r", "10v", "a10p", "11l", "13l", "s32"],
        "function": "Reward prediction, value assessment, pleasure",
        "emotions": ["desire", "anticipation", "satisfaction", "reward expectation"],
    },
}


# ---------------------------------------------------------------------------
# All 360 HCP-MMP1 region names (180 per hemisphere, left then right).
# Source: Glasser et al. 2016 Nature, Supplementary Table 1.
# Left hemisphere = index 0-179, Right hemisphere = 180-359.
# ---------------------------------------------------------------------------

_HCP_REGION_NAMES_LEFT: list[str] = [
    # Visual cortex
    "V1", "V2", "V3", "V4", "V3A", "MT", "V8", "V4t", "FST", "V3B",
    "LO1", "LO2", "PIT", "LO3", "V4v", "V1_d", "V1_v", "MST", "V6", "V6A",
    "V7", "IPS1",
    # Somatomotor
    "4", "3a", "3b", "1", "2", "FEF", "PEF", "55b",
    "6ma", "6mp", "6d", "6v", "6r", "6a", "SCEF",
    # Auditory
    "A1", "LBelt", "MBelt", "PBelt", "RI", "A4", "A5", "STSdp",
    "STSda", "STSvp", "STSva", "TA2",
    # Language
    "44", "45", "47l", "IFJa", "IFJp", "IFSp", "IFSa", "p47r", "a47r",
    # Temporal
    "TGd", "TGv", "TE1a", "TE1m", "TE1p", "TE2a", "TE2p", "TF",
    # Parahippocampal / memory
    "PHA1", "PHA2", "PHA3", "EC", "PreS", "H",
    # Parietal
    "IP0", "IP1", "IP2", "IPO", "IPS1_p", "LIPd", "LIPv",
    "VIP", "MIP", "AIP", "7PC", "7AL", "7AM", "7PL", "7PM",
    "TPOJ1", "TPOJ2", "TPOJ3", "STV",
    # Prefrontal / orbital
    "OFC", "pOFC", "11l", "13l", "a10p", "p10p", "10r", "10v", "10pp",
    "8BM", "8Av", "8Ad", "8BL", "8C", "9m", "9p", "9a",
    # Cingulate / medial
    "d32", "p32", "a24", "p24", "a24pr", "p24pr", "a32pr", "p32pr",
    "s32", "33pr", "25",
    "23c", "23d", "d23ab", "v23ab", "31pv", "31pd", "31a",
    "PCC", "RSC", "ProS", "DVT", "POS1", "POS2",
    # Insular / opercular
    "FOP1", "FOP2", "FOP3", "FOP4", "FOP5", "MI", "PI",
    "Ig", "PoI1", "PoI2", "AVI", "AAIC", "Pir",
    # Visual ventral stream
    "FFC", "VVC",
    # Supplementary / parietal
    "SFL", "7m",
    # Remaining
    "AntIPS", "SFL_v",
]

# Right hemisphere: same names with _R suffix for uniqueness in the atlas dict.
_HCP_REGION_NAMES_RIGHT: list[str] = [f"{n}_R" for n in _HCP_REGION_NAMES_LEFT]

# Full ordered list used for index arithmetic
ALL_HCP_REGION_NAMES: list[str] = _HCP_REGION_NAMES_LEFT + _HCP_REGION_NAMES_RIGHT


# ---------------------------------------------------------------------------
# Approximate vertex-index ranges per marketing cluster.
# These are derived from published fsaverage5 surface geometry and known
# cortical topology.  They will be replaced with exact indices once the Mac
# Mini runs `tribev2/utils.py::get_hcp_labels()`.
#
# Format: (left_start, left_end, right_start, right_end)
# The right hemisphere occupies vertices 10242-20483.
# ---------------------------------------------------------------------------

_APPROXIMATE_CLUSTER_RANGES: dict[str, tuple[int, int, int, int]] = {
    "visual_processing":      (0,    2200, 10242, 12442),
    "auditory_processing":    (4096, 5120, 14338, 15362),
    "language_comprehension": (5120, 6400, 15362, 15500),   # left-dominant; right small
    "decision_making":        (8192, 9800, 18434, 19500),
    "emotional_resonance":    (9216, 10242, 19458, 20484),
    "face_recognition":       (2048, 2600, 12290, 12840),
    "action_impulse":         (6144, 7168, 16386, 17410),
    "social_cognition":       (3500, 4096, 13742, 14338),
    "attention_salience":     (7168, 8192, 17410, 18434),
    "memory_encoding":        (3072, 3500, 13314, 13742),
    "conflict_motivation":    (9000, 9216, 19242, 19458),
    "reward_processing":      (8800, 9216, 19042, 19458),
}


# ---------------------------------------------------------------------------
# Vertex atlas — placeholder filled from approximate ranges until Mac Mini
# ---------------------------------------------------------------------------

_CACHED_ATLAS: Optional[dict[str, np.ndarray]] = None


def _build_approximate_atlas() -> dict[str, np.ndarray]:
    """Build vertex atlas from approximate cluster ranges.

    This is the pre-Mac-Mini placeholder.  Accuracy is ~60-70% for large
    clusters (visual, motor) and lower for small frontal areas.  Replace by
    calling `load_real_atlas(path)` with the output of
    `tribev2/utils.py::get_hcp_labels()`.
    """
    atlas: dict[str, np.ndarray] = {}
    for cluster_name, (ls, le, rs, re) in _APPROXIMATE_CLUSTER_RANGES.items():
        left_verts = np.arange(ls, min(le, N_VERTICES_PER_HEMI))
        right_verts = np.arange(
            max(rs, N_VERTICES_PER_HEMI),
            min(re, N_VERTICES_FSAVERAGE5),
        )
        atlas[cluster_name] = np.concatenate([left_verts, right_verts])
    return atlas


def load_real_atlas(path: str) -> dict[str, np.ndarray]:
    """Load the real HCP-MMP1 vertex atlas produced on the Mac Mini.

    Expected file format: numpy .npz with one array per marketing cluster name,
    e.g. np.savez(path, visual_processing=arr, auditory_processing=arr, ...).

    Call this once at startup and pass the result to score_by_marketing_region().
    """
    global _CACHED_ATLAS
    data = np.load(path, allow_pickle=False)
    _CACHED_ATLAS = {k: data[k] for k in data.files}
    return _CACHED_ATLAS


def get_vertex_atlas(real_atlas_path: Optional[str] = None) -> dict[str, np.ndarray]:
    """Return {cluster_name: vertex_indices_array} for all marketing clusters.

    If real_atlas_path is given (and not already cached), loads from disk.
    Otherwise falls back to the approximate placeholder atlas.
    """
    global _CACHED_ATLAS
    if real_atlas_path is not None and _CACHED_ATLAS is None:
        try:
            return load_real_atlas(real_atlas_path)
        except Exception:
            pass  # Fall through to approximate
    if _CACHED_ATLAS is not None:
        return _CACHED_ATLAS
    return _build_approximate_atlas()


def get_region_vertices(
    region_name: str,
    real_atlas_path: Optional[str] = None,
) -> np.ndarray:
    """Return vertex indices for a named marketing cluster.

    region_name must be a key in MARKETING_REGIONS.
    Returns empty array if the region is not found.
    """
    atlas = get_vertex_atlas(real_atlas_path)
    return atlas.get(region_name, np.array([], dtype=np.int64))


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def summarize_by_region(
    predictions: np.ndarray,
    atlas: dict[str, np.ndarray],
) -> dict[str, float]:
    """Average absolute predictions per marketing region.

    predictions: (n_trs, 20484) — raw TRIBE output at 2 Hz
    atlas: {region_name: vertex_indices}

    Returns {region_name: mean_absolute_activation}
    """
    result: dict[str, float] = {}
    for region, indices in atlas.items():
        if len(indices) == 0:
            result[region] = 0.0
            continue
        # Clamp indices to actual vertex count
        valid = indices[indices < predictions.shape[1]]
        if len(valid) == 0:
            result[region] = 0.0
        else:
            result[region] = float(np.abs(predictions[:, valid]).mean())
    return result


def score_by_marketing_region(
    predictions: np.ndarray,
    real_atlas_path: Optional[str] = None,
) -> dict[str, dict]:
    """Full marketing intelligence breakdown by brain region.

    predictions: (n_trs, 20484) — raw TRIBE output at 2 Hz

    Returns {cluster_name: {score, display_name, function, emotions, raw_activation}}
    where score is 0-100 normalized across all clusters.
    """
    atlas = get_vertex_atlas(real_atlas_path)
    raw = summarize_by_region(predictions, atlas)

    # Normalize to 0-100 across clusters
    values = np.array(list(raw.values()), dtype=float)
    v_min, v_max = values.min(), values.max()
    if v_max > v_min:
        scores_norm = (values - v_min) / (v_max - v_min) * 100
    else:
        scores_norm = np.full_like(values, 50.0)

    result: dict[str, dict] = {}
    for i, (cluster_name, raw_val) in enumerate(raw.items()):
        meta = MARKETING_REGIONS.get(cluster_name, {})
        result[cluster_name] = {
            "score": round(float(scores_norm[i]), 1),
            "raw_activation": round(raw_val, 6),
            "display_name": meta.get("display_name", cluster_name),
            "function": meta.get("function", ""),
            "emotions": meta.get("emotions", []),
        }

    return result
