---
title: TRIBE v2 Inference Pipeline
type: research
tags: [tribe, inference, pipeline, gpu, optimization]
related: [[TRIBE-v2-Architecture]], [[TRIBE-v2-Brain-Regions]], [[Content-Scoring-Framework]]
---

# TRIBE v2 Inference Pipeline

## End-to-End Flow

```
Input Content (video/audio/text)
        |
        v
  [1] Preprocessing
        |
        v
  [2] Feature Extraction (frozen backbones)
        |
        v
  [3] Feature Caching
        |
        v
  [4] Fusion Transformer
        |
        v
  [5] Brain Prediction Head
        |
        v
  [6] Region Aggregation
        |
        v
  [7] Score Computation
        |
        v
  Output: Content Score + Region Breakdown
```

## Step 1: Preprocessing

### Video
- Extract frames at 1 fps (TRIBE temporal resolution is ~0.67 Hz / 1 TR per 1.49s)
- Resize to 224x224 for DINOv2, 384x384 for V-JEPA2
- Normalize with ImageNet mean/std

### Audio
- Extract audio track, resample to 16 kHz mono
- Segment into 1.49-second windows (matching TR)
- No additional normalization (Wav2Vec-BERT handles it)

### Text
- If video has subtitles/captions, extract and align to timestamps
- If audio-only, run Whisper for transcription with word-level timestamps
- Tokenize with LLaMA tokenizer, segment by TR windows

## Step 2: Feature Extraction

### Sequential GPU Loading
Critical for memory management on consumer GPUs:

```
1. Load LLaMA 3.2-3B → extract text features → save to disk → free GPU
2. Load V-JEPA2 ViT-G → extract video features → save to disk → free GPU
3. Load Wav2Vec-BERT 2.0 → extract audio features → save to disk → free GPU
4. Load DINOv2-large → extract image features → save to disk → free GPU
```

Peak VRAM during extraction: ~6 GB (LLaMA phase)

### Feature Dimensions per TR
| Modality | Raw Shape | Projected Shape |
|----------|----------|----------------|
| Text | (seq_len, 2048) -> mean pool | (1, 384) |
| Video | (num_frames, 1280) -> mean pool | (1, 384) |
| Audio | (audio_len, 1024) -> mean pool | (1, 384) |

## Step 3: Feature Caching
Features saved as `.pt` files organized by modality. This allows re-running the fusion model with different hyperparameters without re-extracting features. Cache location: `~/.cache/tribe/features/`

## Step 4: Fusion Transformer
- Load cached features for all modalities
- Concatenate: (batch, 3, 384) — three modality tokens per TR
- Add positional embeddings (temporal position in the 100-TR window)
- Add subject embedding (population average for marketing use)
- Run through 8-layer transformer
- Output: (batch, 100, 1152)

## Step 5: Brain Prediction Head
- Project: 1,152 -> 2,048 (low-rank bottleneck)
- Subject-conditional linear: 2,048 -> 20,484 vertices
- Adaptive average pooling to match input temporal resolution
- Output: (batch, num_TRs, 20484)

## Step 6: Region Aggregation
Map raw vertices to brain regions using the Destrieux atlas:
- Compute mean activation per region per TR
- Compute peak activation per region per TR
- Compute temporal derivatives (rate of change)
- See [[TRIBE-v2-Brain-Regions]] for region-vertex mapping

## Step 7: Score Computation
Apply the [[Content-Scoring-Framework]] to compute:
- Overall score (0-100)
- Hook score (first 3 seconds)
- Modality contribution percentages
- Weak moment timestamps
- Peak moment timestamps

## Performance Benchmarks

### Latency (NVIDIA A100)
| Content Length | Feature Extraction | Fusion + Prediction | Total |
|---------------|-------------------|-------------------|-------|
| 15 seconds | 8s | 0.3s | ~8.3s |
| 60 seconds | 25s | 0.8s | ~25.8s |
| 5 minutes | 95s | 2.5s | ~97.5s |

### Latency (NVIDIA RTX 4090)
| Content Length | Feature Extraction | Fusion + Prediction | Total |
|---------------|-------------------|-------------------|-------|
| 15 seconds | 12s | 0.5s | ~12.5s |
| 60 seconds | 40s | 1.2s | ~41.2s |
| 5 minutes | 150s | 4.0s | ~154s |

### CPU-Only (Apple M3 Max)
| Content Length | Feature Extraction | Fusion + Prediction | Total |
|---------------|-------------------|-------------------|-------|
| 15 seconds | 45s | 2s | ~47s |
| 60 seconds | 180s | 6s | ~186s |

## Batch Processing
For scoring multiple pieces of content:
1. Extract features for all content in sequence (GPU-bound)
2. Run fusion + prediction in batches of 16 (fast)
3. Compute scores in parallel (CPU-bound, trivially parallel)

## Error Handling
- **Missing modality**: Model handles this via modality dropout training. Score is still valid but note which modality was missing.
- **Content too short** (<3 seconds): Pad with zeros. Hook score unreliable.
- **Content too long** (>100 TRs / ~149 seconds): Segment into overlapping windows, average predictions.

## See Also
- [[TRIBE-v2-Architecture]] — Model structure details
- [[TRIBE-Scorer-Agent]] — Agent that runs this pipeline
- [[Content-Scoring-Framework]] — How raw predictions become scores
