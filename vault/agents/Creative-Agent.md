---
title: Creative Agent
type: agent
tags: [agent, creative, generation, content, hooks, scripts]
related: [[Hook-Science]], [[Attention-Curves]], [[Scout-Agent]]
---

# Creative Agent

## Purpose
Generates content concepts, scripts, hooks, and variations informed by brain science patterns. Turns TRIBE intelligence into creative output.

## What It Does
1. **Hook Generation**: Creates multiple hook variations optimized for [[Fusiform-Face-Area]], [[Visual-Cortex]], and [[Prefrontal-Cortex]] activation
2. **Script Writing**: Drafts content scripts structured around optimal [[Attention-Curves]] patterns
3. **Variation Creation**: Produces A/B test variants of hooks, CTAs, thumbnails, and key moments
4. **Format Adaptation**: Transforms content concepts across formats (long-form -> short-form, video -> static)
5. **Trend Response**: Creates content around signals from [[Scout-Agent]]

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `brief` | ContentBrief | Topic, audience, platform, goals |
| `trend_signals` | list[TrendSignal] | From [[Scout-Agent]] |
| `brand_voice` | BrandVoice | Tone, vocabulary, constraints |
| `target_regions` | list[str] | Brain regions to optimize for |
| `num_variations` | int | Number of variants to generate |
| `format` | str | Target format (short-form, long-form, static, etc.) |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `scripts` | list[Script] | Content scripts with timing annotations |
| `hooks` | list[Hook] | Hook variations with predicted brain activation |
| `thumbnails` | list[ThumbnailBrief] | Thumbnail concepts with FFA optimization notes |
| `cta_variants` | list[CTA] | Call-to-action variations |
| `storyboard` | Storyboard | Visual + audio + text timeline |

## API Endpoints Used
- LLM API (Claude/GPT) for text generation
- Image generation API for thumbnail concepts
- Voice synthesis API for audio previews (optional)
- [[TRIBE-Scorer-Agent]] API for pre-scoring concepts

## Knowledge Vault Files Referenced
- [[Hook-Science]] — Hook patterns and benchmarks
- [[Attention-Curves]] — Temporal structure templates
- [[Content-Scoring-Framework]] — Optimization targets
- [[Weak-Moment-Patterns]] — Patterns to avoid
- [[Discovered-Patterns]] — What works based on data
- [[Fusiform-Face-Area]] — Face optimization for thumbnails/hooks
- [[Language-Areas]] — Vocabulary and message optimization
- [[Default-Mode-Network]] — Emotional engagement patterns

## Creative Process
```
1. Receive brief + trend signals
2. Analyze target audience brain response profile
3. Select attention curve archetype (see [[Attention-Curves]])
4. Generate hook variations (3-5 options per piece)
5. Write script following temporal engagement template
6. Mark emotional peaks (DMN activation targets)
7. Mark evaluation moments (PFC activation targets)
8. Place CTA at optimal brain state moment
9. Generate thumbnail concepts optimized for FFA
10. Pre-score all variations with [[TRIBE-Scorer-Agent]]
11. Return ranked variations with predicted scores
```

## Script Annotation Format
The Creative Agent annotates scripts with brain region targets:
```
[0:00-0:03] HOOK — Target: FFA + Visual Cortex
  Face close-up, direct eye contact
  "What if your content could read minds?"
  [Expected: Hook Score 72]

[0:03-0:15] BUILD — Target: Language Areas + PFC
  Problem framing with specific examples
  [Expected: Language activation 65, PFC 55]

[0:15-0:30] PEAK — Target: DMN + Language
  Customer story with emotional resonance
  [Expected: DMN 70, Language 60]

[0:30-0:45] BRIDGE — Target: Visual + Auditory
  B-roll with supporting audio
  [Expected: Visual 60, Auditory 55]

[0:45-0:55] PRIME — Target: PFC
  Question: "What would you do with this?"
  [Expected: PFC 70]

[0:55-1:00] CTA — Target: PFC + DMN
  Clear CTA with emotional + rational framing
  [Expected: PFC 75, DMN 60]
```

## Status Indicators
| Status | Meaning |
|--------|---------|
| `ideating` | Generating concepts from brief + signals |
| `scripting` | Writing full scripts with annotations |
| `varying` | Creating A/B variations |
| `scoring` | Pre-scoring variations with TRIBE |
| `complete` | Outputs ready for review |
| `revision` | Incorporating feedback |

## Handoffs
- Scripts + hooks -> [[TRIBE-Scorer-Agent]] (for brain scoring)
- Scored variations -> [[Optimizer-Agent]] (for refinement)
- Final content -> [[Deployer-Agent]] (for publishing)
- Performance data -> [[Learner-Agent]] (for pattern learning)

## See Also
- [[TRIBE-Scorer-Agent]] — Scores Creative Agent output
- [[Optimizer-Agent]] — Refines based on scores
- [[Scout-Agent]] — Provides trend signals for ideation
- [[Hook-Science]] — Foundation for hook generation
- [[Attention-Curves]] — Structure templates for scripts
