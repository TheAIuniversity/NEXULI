---
title: Modality Analysis
type: knowledge
tags: [modality, visual, audio, text, analysis, contribution]
related: [[Content-Scoring-Framework]], [[Visual-Cortex]], [[Auditory-Cortex]], [[Language-Areas]]
---

# Modality Analysis

## What Is Modality Analysis?
Breaking down a piece of content's brain impact by input channel: visual, audio, and text. TRIBE's modality dropout training means it can isolate each channel's contribution to the predicted brain response.

## How It Works
TRIBE can run inference three ways for the same content:
1. **All modalities** — full prediction (baseline)
2. **Single modality** — zero out other channels, see what one channel contributes
3. **Leave-one-out** — remove one channel, see what drops

The difference between full and leave-one-out gives each modality's marginal contribution.

## Why It Matters
Most content creators optimize only what they can see (visuals) and ignore what they hear (audio) or read (text). Modality analysis reveals the hidden drivers of engagement.

Common surprise findings:
- "Our video performs well because of visuals" -> Actually, 55% of brain response is audio-driven
- "The voiceover carries our podcast" -> 30% of engagement comes from the visual component (facial expressions on video podcast)
- "Our ad copy is strong" -> Language areas are only 12% of total activation; the visual/audio is doing all the work

## Modality Contribution Benchmarks

### By Platform
| Platform | Typical Visual % | Typical Audio % | Typical Text % |
|----------|-----------------|----------------|----------------|
| TikTok/Reels | 50% | 35% | 15% |
| YouTube | 40% | 35% | 25% |
| Podcast (audio) | 0% | 55% | 45% |
| Podcast (video) | 25% | 45% | 30% |
| Instagram Static | 65% | 0% | 35% |
| LinkedIn Post | 30% | 0% | 70% |
| Email | 15% | 0% | 85% |

### By Industry
| Industry | Visual Lean | Audio Lean | Text Lean |
|----------|------------|-----------|----------|
| Fashion/Beauty | Yes | - | - |
| SaaS/Tech | - | - | Yes |
| Food/Beverage | Yes | - | - |
| B2B Services | - | - | Yes |
| Entertainment | Yes | Yes | - |
| Education | - | Yes | Yes |
| Real Estate | Yes | - | - |

## Modality Mismatch Detection

### What Is It?
When modalities are telling different stories or competing for brain resources. Identified by low cross-modal correlation in TRIBE output.

### Common Mismatches
| Mismatch | Symptom | Fix |
|----------|---------|-----|
| Visual-Audio compete | High visual + high auditory but low overall | Simplify one channel |
| Audio-Text redundant | Voiceover reads on-screen text exactly | Differentiate content |
| Visual-Text conflict | Image shows X, text says Y | Align messaging |
| Audio pace vs visual pace | Fast cuts + slow narration | Match pacing |
| Music vs voice compete | Both in same frequency range | Lower music, change key |

### How to Detect
In TRIBE output, check the coherence matrix:
- Visual-Audio correlation > 0.5 = good alignment
- Visual-Audio correlation < 0.3 = potential mismatch
- Language-Prefrontal correlation > 0.4 = message landing
- Language-Prefrontal correlation < 0.2 = comprehension failure

## Modality Optimization Strategies

### Visual-Dominant Content (>50% visual contribution)
- Ensure scene changes every 3-5 seconds
- Include faces (see [[Fusiform-Face-Area]])
- Use motion, not just static frames
- Text overlays should complement, not duplicate audio
- Consider: is audio being wasted? Could it add 20% more engagement?

### Audio-Dominant Content (>50% audio contribution)
- Voice quality is paramount — invest in recording
- Vocal variety (pitch, pace, emphasis) maintains [[Auditory-Cortex]] engagement
- Background music should support, not compete (-12dB relative to voice)
- Consider: are visuals being wasted? Even simple visual support adds engagement
- See [[Auditory-Cortex]] for voice optimization

### Text-Dominant Content (>50% text contribution)
- Vocabulary level must match audience (see [[Language-Areas]])
- Use metaphors to spike angular gyrus
- Questions engage [[Prefrontal-Cortex]] for active processing
- Consider: can visual or audio elements boost the other 50%?

### Balanced Content (no single modality >45%)
- This is the ideal for video content — all channels contributing
- Focus on coherence: all modalities telling the same story
- Use modalities to reinforce, not repeat
- Visual shows what audio/text describes, from a different angle

## Modality Analysis Output Format
```
Content: [filename]
Duration: [seconds]
Overall Score: [0-100]

Modality Breakdown:
  Visual:  [%] ([score])
  Audio:   [%] ([score])
  Text:    [%] ([score])

Coherence: [0-1]
  Visual-Audio: [correlation]
  Audio-Text:   [correlation]
  Visual-Text:  [correlation]

Recommendation: [primary optimization target]
```

## See Also
- [[Content-Scoring-Framework]] — How modality analysis feeds into overall scores
- [[Visual-Cortex]] — Visual channel deep dive
- [[Auditory-Cortex]] — Audio channel deep dive
- [[Language-Areas]] — Text/language channel deep dive
- [[TRIBE-Scorer-Agent]] — Agent that runs modality analysis
