---
title: Attention Curves
type: knowledge
tags: [attention, temporal, engagement, retention, curves]
related: [[Content-Scoring-Framework]], [[Hook-Science]], [[Weak-Moment-Patterns]]
---

# Attention Curves

## What Are Attention Curves?
The temporal profile of brain engagement over the duration of a piece of content. TRIBE produces a per-second (technically per-TR, ~1.49s) engagement score, which when plotted over time creates the "attention curve."

## Anatomy of an Attention Curve

```
Engagement
  100 |     *
   80 |   ** **        **
   60 |  *     ***   **  *        **
   40 | *         * *     **    **  *
   20 |*           *       ****      *
    0 |________________________________
      0s   15s   30s   45s   60s   75s
      Hook  Build  Peak  Dip   Recovery  Close
```

### Key Phases
1. **Hook (0-3s)**: Initial capture. See [[Hook-Science]].
2. **Build (3-15s)**: Establishing context, building interest.
3. **First Peak (15-30s)**: First payoff — insight, emotion, or value delivery.
4. **Mid-Content Dip (30-45s)**: Natural attention regression. Most content loses viewers here.
5. **Recovery (45-60s)**: Re-engagement if content successfully "hooks" again.
6. **Close (final 10s)**: CTA or conclusion. Should ramp up [[Prefrontal-Cortex]].

## Attention Curve Archetypes

### The Ramp (Best for Educational Content)
```
Engagement steadily increases, peaks near the end.
Pattern: Low -> Medium -> High -> Peak at CTA
```
- Works for: Tutorials, how-tos, product demos
- Brain profile: [[Visual-Cortex]] and [[Language-Areas]] build, [[Prefrontal-Cortex]] peaks at end
- Risk: If ramp is too slow, viewers drop before the payoff

### The Mountain (Best for Storytelling)
```
Quick hook, builds to emotional peak mid-content, resolves.
Pattern: High -> Higher -> Peak -> Moderate -> Satisfying close
```
- Works for: Brand stories, testimonials, case studies
- Brain profile: [[Default-Mode-Network]] dominant in peak, [[Prefrontal-Cortex]] at close
- Risk: Anti-climactic endings lose the emotional momentum

### The Rollercoaster (Best for Short-Form)
```
Rapid alternation between peaks and valleys.
Pattern: High -> Low -> High -> Low -> High
```
- Works for: TikTok, Reels, entertaining content
- Brain profile: Multiple [[Visual-Cortex]] spikes, [[Auditory-Cortex]] accents
- Risk: Exhausting for longer content (>60s)

### The Plateau (Neutral — Often Needs Improvement)
```
Moderate engagement maintained throughout.
Pattern: Medium -> Medium -> Medium -> Medium
```
- Common in: Corporate content, webinars, talking heads
- Brain profile: Moderate activation, no strong peaks or drops
- Risk: "Fine but forgettable" — no memorable moments

### The Cliff (Problem Pattern)
```
Strong hook, then rapid decline.
Pattern: High -> Drop -> Low -> Low -> Low
```
- Common in: Clickbait, over-promising hooks
- Brain profile: Initial spike, then [[Default-Mode-Network]] mind-wandering
- Fix: Content must deliver on the hook's promise within 10 seconds

## Per-Region Attention Curves
TRIBE provides attention curves for each brain region independently:

### Visual Attention Curve
- Driven by scene changes, faces, motion
- Naturally has high variance (each visual event spikes)
- Flat visual curve = static visuals, no scene changes
- See [[Visual-Cortex]] for optimization

### Auditory Attention Curve
- Driven by voice, music, sound effects
- More sustained than visual (audio is continuous)
- Drops during silence or monotone speech
- See [[Auditory-Cortex]] for optimization

### Language Processing Curve
- Driven by complexity and novelty of language
- Spikes at new concepts, metaphors, questions
- Flat during filler words or repetitive content
- See [[Language-Areas]] for optimization

### Emotional Engagement Curve (DMN)
- Slower dynamics than sensory regions
- Builds gradually during stories
- Spikes at self-referential moments
- See [[Default-Mode-Network]] for optimization

### Decision/Evaluation Curve (PFC)
- Spikes at questions, comparisons, CTAs
- Should be low during storytelling, high at decision points
- See [[Prefrontal-Cortex]] for optimization

## Optimal Attention Curve by Content Length

### 15 seconds (Short-form)
- Hook at 0-2s (85+ engagement)
- Payoff at 3-10s (70+ sustained)
- CTA at 11-15s (spike back to 80+)
- No room for dips — every second matters

### 60 seconds (Standard social)
- Hook at 0-3s (80+)
- Build at 4-15s (60-70)
- Peak at 15-30s (75+)
- Acceptable dip at 30-40s (50-60, not below 45)
- Recovery at 40-50s (65+)
- CTA at 50-60s (75+)

### 5-10 minutes (Long-form)
- Hook at 0-10s (80+)
- Multiple peaks every 60-90 seconds
- Dips acceptable if >45 and <15 seconds duration
- Re-hooks every 2-3 minutes (mini-hooks)
- Build to strongest peak in final 60 seconds

## Measuring Retention Impact
Attention curve shape correlates with platform retention metrics:

| Curve Shape | Avg Retention at 50% | Avg Completion |
|-------------|---------------------|----------------|
| Ramp | 65% | 55% |
| Mountain | 70% | 60% |
| Rollercoaster | 60% | 45% |
| Plateau | 50% | 40% |
| Cliff | 30% | 15% |

## See Also
- [[Hook-Science]] — Optimizing the first phase of the attention curve
- [[Weak-Moment-Patterns]] — Identifying and fixing the dips
- [[Content-Scoring-Framework]] — How curves feed into overall scores
- [[Optimizer-Agent]] — Agent that recommends curve improvements
