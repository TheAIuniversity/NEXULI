---
title: TRIBE v2 Architecture
type: research
tags: [tribe, architecture, multimodal, transformer]
related: [[TRIBE-v2-Training]], [[TRIBE-v2-Inference-Pipeline]]
---

# TRIBE v2 Architecture

## Overview
TRIBE v2 (TRImodal Brain Encoder) is Meta FAIR's foundation model that predicts whole-brain fMRI responses from video, audio, and text stimuli. Trained on 1,115 hours of brain data across 720 subjects.

## Three-Stage Pipeline

### Stage 1: Frozen Feature Extractors
| Modality | Model | Parameters | Output Dim |
|----------|-------|-----------|-----------|
| Text | LLaMA 3.2-3B | 3B | 2,048 |
| Video | V-JEPA2 ViT-G | 1B | 1,280 |
| Audio | Wav2Vec-BERT 2.0 | 580M | 1,024 |
| Image | DINOv2-large | 300M | - |

All extractors are frozen. Features cached to disk, models freed sequentially.

### Stage 2: Fusion Transformer
- 8-layer Transformer encoder, 8 attention heads
- Hidden dimension: 1,152
- Input: concatenated modality projections (3 x 384)
- Learnable positional + subject embeddings
- Processing window: 100 TRs (~149 seconds)

### Stage 3: Brain Prediction Head
- Low-rank bottleneck: 1,152 -> 2,048
- Subject-conditional linear layer
- Output: 20,484 cortical vertices (fsaverage5)
- Adaptive average pooling to match fMRI temporal resolution

## Key Design Decisions
- **Unimodal extractors over multimodal** — allows modality dropout training
- **Modality dropout (p=0.3)** — randomly zeros entire input channels during training
- **Subject dropout (p=0.1)** — forces shared backbone to learn general features
- **Sequential GPU management** — extract, cache, free, next model

## How the Fusion Works
The fusion transformer is the core innovation. Rather than concatenating features naively, it uses cross-attention between modality tokens. Each modality is projected to a shared 384-dimensional space, then concatenated along the sequence dimension. The transformer's self-attention mechanism learns which modality combinations matter for each brain region.

The modality dropout during training is critical: by randomly zeroing entire modalities, the model learns to predict brain responses from any subset of inputs. This means it can score text-only, audio-only, or video content equally well.

## Subject Conditioning
Each of the 720 training subjects gets a learnable embedding vector. At inference, a new subject can be represented by the average embedding (population-level prediction) or fine-tuned with a few minutes of their data (personalized prediction). For marketing applications, we use population-level predictions since we want to model the average viewer's brain response.

## Memory Footprint
| Component | VRAM |
|-----------|------|
| LLaMA 3.2-3B | ~6 GB |
| V-JEPA2 ViT-G | ~4 GB |
| Wav2Vec-BERT 2.0 | ~2.3 GB |
| DINOv2-large | ~1.2 GB |
| Fusion Transformer | ~2.8 GB |
| **Total (sequential)** | **~8.8 GB peak** |

Sequential loading means peak VRAM is ~8.8 GB (LLaMA + fusion), not the sum of all models.

## Checkpoint
- Size: 709 MB (fusion model only, backbones downloaded separately)
- HuggingFace: `facebook/tribev2`
- License: CC BY-NC 4.0

## See Also
- [[TRIBE-v2-Training]] — How the model was trained
- [[TRIBE-v2-Inference-Pipeline]] — How to run inference
- [[TRIBE-v2-Brain-Regions]] — What the output vertices mean
- [[Meta-FAIR-Papers]] — Source papers
