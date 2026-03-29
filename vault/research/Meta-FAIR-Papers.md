---
title: Meta FAIR Papers
type: reference
tags: [papers, meta, fair, research, citations]
related: [[TRIBE-v2-Architecture]], [[TRIBE-v2-Training]]
---

# Meta FAIR Papers

## Primary TRIBE Paper
**TRIBE: Predicting Brain Activity from Video, Audio, and Text Stimuli**
- Authors: Lahner, B., Dwivedi, K., Sezgin, P., Rawal, R., Girdhar, R., Ballas, N., Muckley, M., et al.
- Venue: Algonauts 2025 Challenge, 1st Place
- Year: 2025
- Link: `https://arxiv.org/abs/2506.xxxxx`

### Key Claims
1. Multimodal brain encoding outperforms unimodal approaches
2. Modality dropout is essential for robust cross-modal generalization
3. Scaling law: performance increases log-linearly with training data
4. Model recovers known neuroscience (face areas, language areas) without supervision

## Backbone Papers

### V-JEPA2 (Video)
**V-JEPA2: Self-Supervised Video Representation Learning**
- Authors: Bardes, A., Garrido, Q., LeCun, Y., et al.
- Year: 2025
- Key idea: Joint-embedding predictive architecture for video. Predicts latent representations of future frames rather than pixel values.
- Why it matters for TRIBE: Captures temporal dynamics, motion patterns, scene transitions — exactly what the visual cortex processes.

### LLaMA 3.2 (Text)
**LLaMA 3: Open Foundation Models**
- Authors: Meta AI
- Year: 2024-2025
- Key idea: 3B parameter language model with strong instruction following.
- Why it matters for TRIBE: Captures semantic meaning, syntax structure, narrative coherence. Maps to language processing areas (Broca's, Wernicke's).

### Wav2Vec-BERT 2.0 (Audio)
**Wav2Vec-BERT 2.0: Robust Speech Representation Learning**
- Authors: Meta FAIR
- Year: 2024
- Key idea: Self-supervised speech model combining wav2vec pretraining with BERT-style masked prediction.
- Why it matters for TRIBE: Captures both speech content and acoustic features (tone, rhythm, emphasis). Maps to auditory cortex.

### DINOv2 (Image)
**DINOv2: Learning Robust Visual Features without Supervision**
- Authors: Oquab, M., Darcet, T., et al.
- Year: 2023
- Key idea: Self-supervised visual features that transfer across tasks. ViT-Large with 300M parameters.
- Why it matters for TRIBE: Captures object identity, scene layout, visual semantics. Supplements V-JEPA2 for per-frame analysis.

## Related Brain Encoding Work

### BrainBench
**BrainBench: A Benchmark for Brain Encoding Models**
- Year: 2024
- Relevance: Standard evaluation protocol that TRIBE v2 surpasses on all metrics.

### Brain Diffuser
**Brain Diffuser: Generating Images from Brain Activity**
- Year: 2023
- Relevance: Inverse direction (brain -> content). Validates that brain-content mapping is learnable.

### Algonauts 2023
**The Algonauts Project 2023: How the Brain Makes Sense of Natural Scenes**
- Year: 2023
- Relevance: Predecessor challenge. TRIBE v1 concepts emerged from this competition.

## Neuroscience Foundations

### fMRI and BOLD Signal
- BOLD (Blood-Oxygen-Level-Dependent) signal is an indirect measure of neural activity
- Temporal resolution: ~1.49 seconds per TR (repetition time)
- Spatial resolution: ~2mm (raw) -> 20,484 vertices (fsaverage5 surface)
- Hemodynamic delay: neural activity peaks in BOLD ~5-6 seconds later

### fsaverage5 Surface
- Standard surface mesh with 10,242 vertices per hemisphere
- Total: 20,484 cortical vertices
- Based on Freesurfer cortical surface reconstruction
- Allows comparison across subjects by projecting individual brains onto a common template

### Destrieux Atlas
- 148 cortical regions (74 per hemisphere)
- Used by TRIBE to aggregate vertex-level predictions into region scores
- Standard neuroanatomical parcellation

## Reading Order
For understanding TRIBE from scratch:
1. fsaverage5 surface and BOLD signal basics
2. DINOv2 paper (simplest backbone)
3. V-JEPA2 paper (video understanding approach)
4. TRIBE primary paper
5. [[TRIBE-v2-Architecture]] for implementation details

## See Also
- [[TRIBE-v2-Architecture]] — How these papers come together in the model
- [[TRIBE-v2-Training]] — Training details and competition results
- [[TRIBE-v2-Brain-Regions]] — Neuroscience grounding
