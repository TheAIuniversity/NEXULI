---
title: TRIBE v2 Training
type: research
tags: [tribe, training, fmri, datasets]
related: [[TRIBE-v2-Architecture]]
---

# TRIBE v2 Training

## Training Data
- **451.6 hours of fMRI** from 25 subjects across 4 studies
- **1,117.7 hours evaluation** across 720 subjects
- Studies: Algonauts2025Bold (Friends + movies), Lahner2024Bold (video clips), Lebel2023Bold (spoken narratives), Wen2017 (videos)

### Dataset Breakdown
| Study | Subjects | Hours | Content Type |
|-------|----------|-------|-------------|
| Algonauts2025Bold | 8 | 180.2 | Friends episodes + movies |
| Lahner2024Bold | 3 | 45.8 | Short video clips |
| Lebel2023Bold | 8 | 156.4 | Spoken narratives (audio-only) |
| Wen2017 | 6 | 69.2 | Movie clips |

### Why These Datasets Matter
The diversity of content types forces the model to learn general brain encoding rather than overfitting to one modality. Lebel2023Bold is audio-only narratives, which teaches the model how language alone drives brain responses. Lahner2024Bold has short clips with rapid scene changes, teaching visual attention dynamics.

## Training Configuration
- Loss: MSE (mean squared error on vertex-level predictions)
- Optimizer: Adam, lr=1e-4
- Scheduler: OneCycleLR, 10% warmup
- Epochs: 15
- Batch size: 16
- Modality dropout: 0.3
- Subject dropout: 0.1
- Gradient clipping: max norm 1.0
- Weight decay: 0.01

### Training Tricks
- **Modality dropout (p=0.3)**: Each modality independently zeroed with 30% probability per batch. Forces the model to never rely on a single modality.
- **Subject dropout (p=0.1)**: Subject embedding replaced with zero vector 10% of the time. Prevents the model from memorizing subject-specific quirks.
- **Mixed precision (bf16)**: Reduces memory, allows larger batch sizes.
- **Feature caching**: All frozen backbone features pre-extracted and saved to disk. Training only touches the fusion transformer and prediction head.

## Competition Results (Algonauts 2025)
- **1st place** out of 263 teams
- Mean score: 0.2146 (Pearson correlation between predicted and actual fMRI)
- Ensemble: 1,000 models with per-parcel softmax weighting

### What "0.2146 Pearson correlation" Means
This is the average correlation across all 20,484 cortical vertices. Some regions are far more predictable:
- Visual cortex: r ~ 0.5-0.7 (highly predictable from video)
- Auditory cortex: r ~ 0.4-0.6 (highly predictable from audio)
- Prefrontal cortex: r ~ 0.1-0.2 (harder to predict, more individual variation)
- Default mode network: r ~ 0.15-0.25 (emotion/self-reference is noisy)

### Ensemble Strategy
The winning submission averaged 1,000 independently trained models, each with different random seeds and modality dropout patterns. Per-parcel softmax weighting means each brain region gets its own optimal model blend.

## Scaling Law
Performance scales **log-linearly** with training data — no plateau observed. Same power law as LLMs.

```
Performance ~ a * log(data_hours) + b
```

This means every doubling of training data gives a consistent improvement. The implication: future versions with more fMRI data will be meaningfully better.

## Key Validation
Model recovers known neuroscience without being told:
- Fusiform Face Area activates for faces
- Broca's Area activates for syntax
- ICA reveals 5 canonical brain networks spontaneously
- Tonotopic maps in auditory cortex match known frequency organization
- Retinotopic maps in visual cortex match known spatial organization

This is the strongest evidence that TRIBE actually learns something real about how the brain processes stimuli — it rediscovers decades of neuroscience from raw data.

## See Also
- [[TRIBE-v2-Architecture]] — Model structure
- [[TRIBE-v2-Brain-Regions]] — Brain region mapping
- [[Content-Scoring-Framework]] — How training insights inform scoring
