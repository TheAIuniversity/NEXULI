---
title: TRIBE Scorer Agent
type: agent
tags: [agent, scorer, tribe, fmri, brain, scoring]
related: [[Content-Scoring-Framework]], [[TRIBE-v2-Architecture]], [[TRIBE-v2-Inference-Pipeline]]
---

# TRIBE Scorer Agent

## Purpose
Runs the TRIBE v2 inference pipeline on content and produces brain-based scores, region breakdowns, attention curves, and optimization recommendations.

## What It Does
1. **Content Ingestion**: Accepts video, audio, and/or text content for analysis
2. **Feature Extraction**: Runs frozen backbone extractors (LLaMA, V-JEPA2, Wav2Vec-BERT, DINOv2)
3. **Brain Prediction**: Runs fusion transformer + prediction head to generate vertex-level brain activations
4. **Score Computation**: Applies [[Content-Scoring-Framework]] to produce marketing-relevant scores
5. **Region Analysis**: Breaks down activation by brain region with marketing interpretation
6. **Temporal Analysis**: Produces attention curves and identifies weak/peak moments
7. **Modality Analysis**: Determines contribution of each input channel

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `content_path` | str | Path to video/audio file |
| `text_content` | str | Optional text/script content |
| `content_type` | str | Type: video, audio, text, image |
| `duration_seconds` | float | Content duration |
| `context` | dict | Platform, audience, goals |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `overall_score` | float | 0-100 weighted score |
| `hook_score` | float | 0-100 first 3 seconds |
| `region_scores` | dict | Per-region activation scores |
| `modality_breakdown` | dict | Visual %, Audio %, Text % |
| `attention_curve` | list[float] | Per-second engagement scores |
| `weak_moments` | list[WeakMoment] | Drops with causes and fixes |
| `peak_moments` | list[PeakMoment] | Peaks with best-use tags |
| `coherence_score` | float | Cross-modal alignment |
| `recommendations` | list[str] | Specific optimization suggestions |

## API Endpoints Used
- TRIBE v2 model inference (local GPU or cloud endpoint)
- HuggingFace Hub (for model weights: `facebook/tribev2`)
- Feature extraction endpoints (LLaMA, V-JEPA2, Wav2Vec-BERT, DINOv2)
- FFmpeg for media preprocessing

## Knowledge Vault Files Referenced
- [[TRIBE-v2-Architecture]] — Model architecture understanding
- [[TRIBE-v2-Inference-Pipeline]] — Step-by-step inference process
- [[TRIBE-v2-Brain-Regions]] — Vertex-to-region mapping
- [[Content-Scoring-Framework]] — Score computation methodology
- [[Weak-Moment-Patterns]] — Weak moment classification rules
- [[Attention-Curves]] — Attention curve archetype matching
- [[Modality-Analysis]] — Modality contribution analysis

## Scoring Pipeline
```
1. Receive content
2. Preprocess:
   - Extract video frames (1 fps)
   - Extract audio (16 kHz mono)
   - Extract/generate text (subtitles or Whisper transcription)
3. Feature extraction (sequential GPU loading):
   a. LLaMA 3.2-3B -> text features -> cache -> free
   b. V-JEPA2 ViT-G -> video features -> cache -> free
   c. Wav2Vec-BERT 2.0 -> audio features -> cache -> free
   d. DINOv2-large -> image features -> cache -> free
4. Load fusion transformer
5. Run fusion on cached features
6. Run brain prediction head
7. Aggregate vertices to regions
8. Apply scoring framework
9. Generate attention curve
10. Identify weak moments + peak moments
11. Compute modality breakdown
12. Generate recommendations
13. Return complete score report
```

## Output Report Format
```json
{
  "overall_score": 72,
  "hook_score": 81,
  "region_scores": {
    "visual_cortex": 68,
    "auditory_cortex": 74,
    "language_areas": 65,
    "prefrontal_cortex": 71,
    "default_mode_network": 58,
    "fusiform_face_area": 82
  },
  "modality_breakdown": {
    "visual": 42,
    "audio": 35,
    "text": 23
  },
  "attention_curve": [82, 79, 78, 71, 65, ...],
  "weak_moments": [
    {
      "start_s": 22,
      "end_s": 28,
      "severity": "mild",
      "root_cause": "visual_cortex_flat",
      "fix": "Add scene change or B-roll at 22-28s"
    }
  ],
  "peak_moments": [
    {
      "start_s": 0,
      "end_s": 3,
      "score": 81,
      "best_use": "hook"
    }
  ],
  "coherence_score": 0.72,
  "recommendations": [
    "Strong hook - face + question pattern working well",
    "Add visual variety at 22-28s to address mild weak moment",
    "Language areas could be higher - simplify vocabulary in middle section"
  ]
}
```

## Status Indicators
| Status | Meaning |
|--------|---------|
| `preprocessing` | Extracting video/audio/text streams |
| `extracting_features` | Running frozen backbone models |
| `predicting` | Running fusion transformer + prediction head |
| `scoring` | Computing scores from raw predictions |
| `analyzing` | Generating weak/peak moments and recommendations |
| `complete` | Full report ready |
| `error` | Pipeline failure (with error details) |
| `queued` | Waiting for GPU availability |

## Performance
- 15-second content: ~12 seconds on RTX 4090, ~8 seconds on A100
- 60-second content: ~41 seconds on RTX 4090, ~26 seconds on A100
- Batch mode: Up to 16 items in parallel on fusion step

## Handoffs
- Receives content from [[Creative-Agent]] and [[Scout-Agent]]
- Score reports -> [[Optimizer-Agent]] (for refinement suggestions)
- Score reports -> [[Learner-Agent]] (for pattern learning)
- Score reports -> Dashboard (for user visibility)
- Historical scores -> [[Calibration-Log]]

## See Also
- [[TRIBE-v2-Architecture]] — Underlying model
- [[Content-Scoring-Framework]] — Scoring methodology
- [[Optimizer-Agent]] — Uses scores to recommend improvements
- [[Content-Score-Template]] — Template for recording results
