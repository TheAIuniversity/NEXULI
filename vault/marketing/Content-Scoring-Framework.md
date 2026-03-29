---
title: Content Scoring Framework
type: framework
tags: [scoring, methodology, tribe]
related: [[Attention-Curves]], [[Modality-Analysis]], [[Hook-Science]]
---

# Content Scoring Framework

## How TRIBE Scores Map to Marketing Metrics

### Overall Score (0-100)
Weighted combination:
- 25% Visual cortex activation ([[Visual-Cortex]])
- 20% Auditory cortex activation ([[Auditory-Cortex]])
- 20% Language processing (Broca's + Wernicke's) ([[Language-Areas]])
- 20% Prefrontal activation (decision-making) ([[Prefrontal-Cortex]])
- 15% Default mode network (emotion/self-reference) ([[Default-Mode-Network]])

### Score Interpretation
| Score | Rating | Meaning |
|-------|--------|---------|
| 0-20 | Very Weak | Content fails to engage any brain region meaningfully |
| 20-40 | Below Average | One or two regions activated but not cohesively |
| 40-60 | Average | Adequate engagement, room for significant improvement |
| 60-75 | Strong | Good multi-region engagement, minor optimizations possible |
| 75-90 | Excellent | Broad, sustained brain engagement across regions |
| 90-100 | Exceptional | Rare — all regions activated in optimal sequence |

### Modality Contribution
Percentage of total brain response driven by each input channel:
- Visual %: visual cortex share of total activation
- Audio %: auditory cortex share of total activation
- Text %: language areas share of total activation

Ideal distribution depends on content type:
| Content Type | Visual % | Audio % | Text % |
|-------------|---------|--------|--------|
| Short-form video (TikTok/Reels) | 45-55 | 30-35 | 15-20 |
| Long-form video (YouTube) | 35-45 | 30-40 | 20-30 |
| Podcast with video | 20-30 | 40-50 | 25-35 |
| Static ad with copy | 50-60 | 0 | 40-50 |
| Webinar/presentation | 25-35 | 35-45 | 25-35 |

### Hook Score
Average attention in first 3 seconds. Critical for social media (scroll-stop).

Computed from:
- [[Fusiform-Face-Area]] activation (face detection)
- [[Visual-Cortex]] activation (visual salience)
- [[Auditory-Cortex]] onset response (audio grab)
- [[Prefrontal-Cortex]] spike (curiosity/evaluation trigger)

See [[Hook-Science]] for detailed hook optimization.

### Weak Moments
Consecutive seconds where attention < 40. Each tagged with:
- Root cause (which brain region dropped)
- Specific fix recommendation
- Timestamp range
- Severity (mild: 30-40, moderate: 20-30, severe: <20)

See [[Weak-Moment-Patterns]] for common patterns and fixes.

### Peak Moments
Consecutive seconds where attention > 80. Tagged with best use:
- "hook" — strong opening material, can be repurposed as content hook
- "thumbnail" — best visual frame (highest [[Fusiform-Face-Area]] activation)
- "clip" — extract for short-form content repurposing
- "quote" — highest [[Language-Areas]] activation, memorable statement
- "cta-moment" — highest [[Prefrontal-Cortex]] activation, optimal conversion point

## Score Components Deep Dive

### Engagement Score
Raw activation intensity across all regions. Answers: "Is the brain paying attention?"

### Coherence Score
Cross-modal correlation — do visual, audio, and text activations support each other? High coherence = unified message. Low coherence = modality mismatch.

Calculation: Pearson correlation between visual cortex and auditory cortex time series, averaged with language-prefrontal correlation.

### Emotional Resonance Score
[[Default-Mode-Network]] activation normalized by content length. Answers: "Does this content connect personally?"

### Purchase Intent Proxy
[[Prefrontal-Cortex]] activation during CTA moments, modulated by [[Default-Mode-Network]] co-activation. Answers: "Is the viewer in a state to take action?"

### Memorability Index
Peak [[Default-Mode-Network]] activation * [[Language-Areas]] activation at key message moments. Answers: "Will the viewer remember this?"

## Calibration
Scores are calibrated against a reference dataset of 10,000 scored pieces of content across industries. Calibration is logged in [[Calibration-Log]] and updated monthly.

Raw TRIBE predictions are transformed to the 0-100 scale using:
1. Z-score normalization against reference distribution
2. Sigmoid mapping to 0-100
3. Industry-specific adjustment (B2B content naturally scores lower on visual cortex)

## See Also
- [[Hook-Science]] — Hook score methodology
- [[Weak-Moment-Patterns]] — Weak moment detection and fixes
- [[Attention-Curves]] — Temporal dynamics of scores
- [[Modality-Analysis]] — Modality contribution analysis
- [[TRIBE-Scorer-Agent]] — Agent that computes these scores
- [[Content-Score-Template]] — Template for recording scores
