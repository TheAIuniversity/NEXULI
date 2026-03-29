"""
Context Compression — reduce token costs when agents pass data around.
Pattern stolen from ClawRouter's 7-layer compression pipeline.
"""

import re
import json
import hashlib
from typing import List, Dict

# Dictionary compression — common phrases get shortened
DICTIONARY = {
    "content scored": "«CS»",
    "overall score": "«OS»",
    "attention curve": "«AC»",
    "visual cortex": "«VC»",
    "auditory cortex": "«AuC»",
    "prefrontal cortex": "«PFC»",
    "default mode network": "«DMN»",
    "fusiform face area": "«FFA»",
    "language areas": "«LA»",
    "weak moment": "«WM»",
    "peak moment": "«PM»",
    "hook score": "«HS»",
    "modality mix": "«MM»",
    "recommendation": "«REC»",
    "competitor": "«COMP»",
    "brain region": "«BR»",
}

REVERSE_DICTIONARY = {v: k for k, v in DICTIONARY.items()}


def compress_context(data: dict | str, level: int = 3) -> str:
    """Compress context data to reduce token count.

    Levels:
    1 - Whitespace normalization only
    2 - + JSON compaction
    3 - + Dictionary substitution
    4 - + Observation compression (keep only key fields)
    5 - + Aggressive truncation

    Returns compressed string with codebook header if dictionary was used.
    """
    if isinstance(data, dict):
        text = json.dumps(data)
    else:
        text = data

    original_len = len(text)

    # Level 1: Whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Level 2: JSON compaction
    if level >= 2:
        try:
            parsed = json.loads(text)
            text = json.dumps(parsed, separators=(",", ":"))
        except (json.JSONDecodeError, TypeError):
            pass

    # Level 3: Dictionary substitution
    codebook_used = False
    if level >= 3:
        for phrase, code in DICTIONARY.items():
            if phrase.lower() in text.lower():
                text = re.sub(re.escape(phrase), code, text, flags=re.IGNORECASE)
                codebook_used = True

    # Level 4: Observation compression — keep only essential fields from score results
    if level >= 4:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                parsed = _compress_score_result(parsed)
                text = json.dumps(parsed, separators=(",", ":"))
        except (json.JSONDecodeError, TypeError):
            pass

    # Level 5: Truncation
    if level >= 5 and len(text) > 2000:
        text = text[:2000] + "…[truncated]"

    # Prepend codebook if dictionary was used
    if codebook_used:
        used_codes = {code: phrase for phrase, code in DICTIONARY.items() if code in text}
        if used_codes:
            header = "CODEBOOK:" + "|".join(f"{c}={p}" for c, p in used_codes.items())
            text = header + "\n" + text

    compressed_len = len(text)
    savings = round((1 - compressed_len / max(original_len, 1)) * 100, 1)

    return text


def decompress_context(text: str) -> str:
    """Decompress a compressed context string back to readable form."""
    # Remove codebook header
    if text.startswith("CODEBOOK:"):
        text = text.split("\n", 1)[1] if "\n" in text else text

    # Reverse dictionary
    for code, phrase in REVERSE_DICTIONARY.items():
        text = text.replace(code, phrase)

    return text


def _compress_score_result(data: dict) -> dict:
    """Compress a TRIBE score result to essential fields only.

    ClawRouter's observation pattern: keep status, errors, key metrics.
    Drop verbose per-second data.
    """
    compressed = {}

    # Keep key metrics
    for key in [
        "overall_score", "duration_seconds", "hook_score",
        "visual_pct", "audio_pct", "text_pct",
        "visual_avg", "auditory_avg", "language_avg",
        "decision_avg", "emotion_avg",
    ]:
        if key in data:
            compressed[key] = data[key]

    # Compress per_second to just the attention values (drop per-region detail)
    if "per_second" in data and isinstance(data["per_second"], list):
        compressed["attention_curve"] = [
            round(s["attention"], 1) if isinstance(s, dict) else round(s, 1)
            for s in data["per_second"]
        ]

    # Keep weak/peak moments but compress
    if "weak_moments" in data:
        compressed["weak"] = [
            {"t": f"{w['start']:.0f}-{w['end']:.0f}", "fix": w.get("recommendation", "")}
            for w in data["weak_moments"]
        ]

    if "peak_moments" in data:
        compressed["peak"] = [
            {"t": f"{p['start']:.0f}-{p['end']:.0f}", "use": p.get("use_case", "")}
            for p in data["peak_moments"]
        ]

    return compressed


def estimate_tokens(text: str) -> int:
    """Rough token count estimation (1 token ≈ 4 chars for English)."""
    return len(text) // 4
