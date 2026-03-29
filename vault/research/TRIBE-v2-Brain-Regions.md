---
title: TRIBE v2 Brain Regions
type: research
tags: [tribe, brain, cortex, vertices, fsaverage5]
related: [[TRIBE-v2-Architecture]], [[Visual-Cortex]], [[Auditory-Cortex]], [[Language-Areas]], [[Prefrontal-Cortex]], [[Default-Mode-Network]], [[Fusiform-Face-Area]]
---

# TRIBE v2 Brain Regions

## Output Space
TRIBE v2 predicts activation for **20,484 cortical vertices** on the fsaverage5 surface mesh. These vertices map to known brain regions that process different aspects of stimuli.

## Region-to-Vertex Mapping

### Major Regions
| Region | Approximate Vertices | Primary Function | Marketing Relevance |
|--------|---------------------|-----------------|-------------------|
| Visual Cortex (V1-V3) | 0-2,048 | Edge, color, motion | Visual engagement |
| Auditory Cortex | 2,049-3,584 | Sound processing | Audio quality/impact |
| Language Areas | 3,585-5,120 | Syntax, semantics | Message comprehension |
| Prefrontal Cortex | 5,121-8,192 | Decision-making | Purchase intent |
| Default Mode Network | 8,193-11,264 | Self-reference, emotion | Emotional resonance |
| Fusiform Face Area | 11,265-12,288 | Face processing | Talent/presenter impact |
| Motor Cortex | 12,289-14,336 | Movement planning | Action/CTA response |
| Temporal Pole | 14,337-15,360 | Social/emotional context | Story engagement |
| Parietal Cortex | 15,361-17,408 | Spatial attention | Layout/composition |
| Insular Cortex | 17,409-18,432 | Disgust, empathy | Emotional intensity |
| Other regions | 18,433-20,484 | Various | Contextual |

> **Note**: Vertex ranges are approximate and based on the Destrieux atlas parcellation projected onto fsaverage5. Actual boundaries are probabilistic.

## How to Read TRIBE Output
The raw output is a time series of 20,484 values per TR (1.49 seconds). Each value represents predicted BOLD signal change — how much blood flow (and thus neural activity) that vertex would show.

### Aggregation for Marketing
We aggregate raw vertices into region-level scores:
1. **Mean activation**: Average across vertices in a region
2. **Peak activation**: Maximum vertex value in a region
3. **Temporal variance**: How much activation changes over time (engagement dynamics)
4. **Cross-region correlation**: Which regions fire together (multimodal coherence)

## Region Interactions That Matter

### Visual-Auditory Coherence
When visual and auditory cortex activations are temporally correlated (r > 0.6), content feels "coherent" — audio matches visual. Low correlation means audio-visual mismatch, which reduces engagement.

### Prefrontal-Default Mode Anti-Correlation
These networks typically anti-correlate: when one is active, the other suppresses. Content that breaks this pattern (both active simultaneously) tends to be highly engaging — the viewer is both emotionally involved AND actively evaluating.

### Language-Prefrontal Chain
Language areas activate first (comprehension), then prefrontal activates (evaluation). The delay between them indicates processing depth. Short delay = simple message. Long delay = complex message requiring more thought.

## Predictability by Region
| Region | Pearson r | Predictability |
|--------|----------|---------------|
| Visual Cortex | 0.5-0.7 | Excellent |
| Auditory Cortex | 0.4-0.6 | Very Good |
| Language Areas | 0.3-0.5 | Good |
| Fusiform Face Area | 0.4-0.6 | Very Good |
| Default Mode Network | 0.15-0.25 | Moderate |
| Prefrontal Cortex | 0.1-0.2 | Lower |

Higher predictability means we can trust TRIBE scores more for that region.

## See Also
- [[Visual-Cortex]] — Detailed visual cortex documentation
- [[Auditory-Cortex]] — Detailed auditory cortex documentation
- [[Language-Areas]] — Detailed language areas documentation
- [[Prefrontal-Cortex]] — Detailed prefrontal cortex documentation
- [[Default-Mode-Network]] — Detailed DMN documentation
- [[Fusiform-Face-Area]] — Detailed FFA documentation
- [[Content-Scoring-Framework]] — How regions map to scores
