---
title: Discovered Patterns
type: patterns
tags: [patterns, discoveries, rules, validated, living-document]
related: [[Calibration-Log]], [[Learner-Agent]], [[Content-Scoring-Framework]]
---

# Discovered Patterns

> **Living document.** Updated by [[Learner-Agent]] as new patterns are discovered and validated. Last updated: 2026-03-28.

## Pattern Format
Each pattern includes:
- **Pattern**: What was observed
- **Brain Signature**: Which brain regions and what activation pattern
- **Effect Size**: How much impact (validated against real performance data)
- **Confidence**: How many data points validated this
- **Applicable To**: Content types and platforms where this holds

---

## Hook Patterns

### H-001: Face in First 2 Seconds
- **Pattern**: Face in first 2 seconds -> +40% [[Fusiform-Face-Area]] activation
- **Brain Signature**: FFA spike within 200ms of face appearance, cascading to DMN (social cognition) within 500ms
- **Effect Size**: +40% FFA activation, +18% retention at 3 seconds
- **Confidence**: High (n=842 content pieces)
- **Applicable To**: All video content, all platforms

### H-002: Direct Eye Contact
- **Pattern**: Direct eye contact in opening -> +25% FFA vs. profile view
- **Brain Signature**: FFA + amygdala co-activation (eye contact triggers threat/social evaluation pathway)
- **Effect Size**: +25% FFA, +12% scroll-stop rate
- **Confidence**: High (n=623)
- **Applicable To**: Short-form video, thumbnails

### H-003: Question Opening
- **Pattern**: Opening with a specific question -> +35% [[Prefrontal-Cortex]] activation
- **Brain Signature**: PFC spike (evaluation mode) + language areas (comprehension)
- **Effect Size**: +35% PFC, +15% retention at 10 seconds
- **Confidence**: High (n=531)
- **Applicable To**: All video/audio, LinkedIn text posts

### H-004: Audio-First Hook
- **Pattern**: Voice starting in first 0.5 seconds -> +22% [[Auditory-Cortex]] vs. music intro
- **Brain Signature**: Auditory cortex onset response, faster handoff to language areas
- **Effect Size**: +22% auditory activation, +9% retention at 3 seconds
- **Confidence**: Medium-High (n=387)
- **Applicable To**: Video with audio, podcasts

### H-005: Pattern Interrupt
- **Pattern**: High-contrast visual change in first second -> +28% [[Visual-Cortex]] spike
- **Brain Signature**: V1/V2 spike (novelty detection), brief orienting response
- **Effect Size**: +28% visual cortex, +11% scroll-stop rate
- **Confidence**: Medium-High (n=294)
- **Applicable To**: Short-form video, ads

---

## Engagement Patterns

### E-001: Scene Change Cadence
- **Pattern**: Scene changes every 4 seconds maintain [[Visual-Cortex]] engagement
- **Brain Signature**: V1/V2 re-activation spike every 4 seconds, preventing visual cortex flatline
- **Effect Size**: +32% visual cortex mean activation vs. static shots
- **Confidence**: High (n=712)
- **Applicable To**: All video content

### E-002: Vocal Variety Window
- **Pattern**: Monotone voice causes [[Auditory-Cortex]] flatline within 8-10 seconds
- **Brain Signature**: Auditory cortex habituates to constant pitch/pace, activation declines exponentially
- **Effect Size**: -45% auditory activation after 10 seconds of monotone
- **Confidence**: High (n=445)
- **Applicable To**: All voice-forward content

### E-003: Metaphor Spike
- **Pattern**: Metaphors activate angular gyrus 30% more than literal equivalents
- **Brain Signature**: Angular gyrus spike (cross-modal mapping) + brief PFC activation (novelty processing)
- **Effect Size**: +30% angular gyrus, +8% message recall
- **Confidence**: Medium (n=256)
- **Applicable To**: Scripted content, copywriting

### E-004: Background Music Sweet Spot
- **Pattern**: Background music at -12dB relative to voice optimizes engagement
- **Brain Signature**: Auditory cortex supports voice processing without competing; no language area interference
- **Effect Size**: +12% overall engagement vs. no music, no loss vs. voice-only
- **Confidence**: Medium-High (n=318)
- **Applicable To**: Video with voiceover, podcast with music

### E-005: Emotional Music Without Lyrics
- **Pattern**: Instrumental music activates [[Default-Mode-Network]] without competing with [[Language-Areas]]
- **Brain Signature**: DMN activation (emotional processing) maintained while language areas process speech
- **Effect Size**: +18% emotional resonance score vs. music with lyrics
- **Confidence**: Medium (n=203)
- **Applicable To**: Video with voiceover, brand storytelling

---

## Modality Patterns

### M-001: Audio-Dominant B2B
- **Pattern**: Audio-dominant content converts 2.1x for B2B audiences
- **Brain Signature**: B2B audiences show higher language area + PFC activation from audio channel than visual
- **Effect Size**: 2.1x conversion rate when audio contribution > 45%
- **Confidence**: Medium (n=178)
- **Applicable To**: B2B content, LinkedIn, webinars

### M-002: Visual-Audio Coherence
- **Pattern**: High visual-audio correlation (r > 0.6) -> +25% overall engagement
- **Brain Signature**: Cross-modal correlation indicates unified message processing
- **Effect Size**: +25% engagement vs. low coherence (r < 0.3)
- **Confidence**: High (n=589)
- **Applicable To**: All video content

### M-003: Modality Mismatch Penalty
- **Pattern**: Voiceover reading on-screen text exactly -> -15% [[Language-Areas]] activation
- **Brain Signature**: Redundant dual-channel input causes processing inefficiency
- **Effect Size**: -15% language activation, -8% information retention
- **Confidence**: Medium-High (n=267)
- **Applicable To**: Video with text overlays and voiceover

---

## Conversion Patterns

### C-001: PFC-DMN Convergence
- **Pattern**: When [[Prefrontal-Cortex]] and [[Default-Mode-Network]] are both active at CTA moment -> 3.2x conversion
- **Brain Signature**: Normally anti-correlated networks both positive — "I want this AND I can justify it"
- **Effect Size**: 3.2x conversion rate vs. PFC-only active at CTA
- **Confidence**: Medium (n=142)
- **Applicable To**: All content with CTA

### C-002: Question Before CTA
- **Pattern**: Question 3-5 seconds before CTA -> +40% PFC activation at CTA moment
- **Brain Signature**: Question primes PFC (evaluation mode), which persists through CTA
- **Effect Size**: +40% PFC at CTA, +22% click-through
- **Confidence**: Medium-High (n=289)
- **Applicable To**: All content with CTA

### C-003: Testimonial Trust Signal
- **Pattern**: Authentic testimonial activates lateral temporal cortex (social cognition) but NOT ACC (conflict detection)
- **Brain Signature**: Social processing without skepticism signal = trust
- **Effect Size**: +35% conversion vs. scripted-sounding testimonial (which triggers ACC)
- **Confidence**: Medium (n=167)
- **Applicable To**: Testimonial/social proof content

### C-004: Transformation Story Before CTA
- **Pattern**: Before/after transformation activates hippocampus (future self-projection) -> +28% CTA response
- **Brain Signature**: Hippocampal formation activation (imagining future self in the "after" state)
- **Effect Size**: +28% CTA click-through
- **Confidence**: Medium (n=134)
- **Applicable To**: Fitness, SaaS, education, coaching content

---

## Thumbnail Patterns

### T-001: Emotional Face Thumbnail
- **Pattern**: Close-up face with surprise/curiosity expression -> +45% CTR vs. no-face thumbnail
- **Brain Signature**: FFA spike drives initial attention capture in thumbnail context
- **Effect Size**: +45% CTR
- **Confidence**: High (n=923)
- **Applicable To**: YouTube, all thumbnail contexts

### T-002: Face + Text Combo
- **Pattern**: Face on one side + 3-5 word text on other -> optimal thumbnail activation
- **Brain Signature**: FFA processes face while language areas process text — dual engagement
- **Effect Size**: +52% CTR vs. text-only, +15% vs. face-only
- **Confidence**: Medium-High (n=341)
- **Applicable To**: YouTube thumbnails

---

## Anti-Patterns (What NOT To Do)

### AP-001: Logo Intro
- **Pattern**: Animated logo intro in first 3 seconds -> -35% hook score
- **Brain Signature**: Only brief visual cortex activation, no FFA, no PFC, no DMN
- **Effect Size**: -35% hook score, -25% retention at 5 seconds
- **Confidence**: High (n=456)
- **Applicable To**: All video content

### AP-002: Stock Footage Uncanny Valley
- **Pattern**: Obvious stock footage triggers ACC (conflict detection) -> trust penalty
- **Brain Signature**: Visual cortex + ACC co-activation ("I see something but it feels wrong")
- **Effect Size**: -18% trust score, -12% conversion
- **Confidence**: Medium (n=198)
- **Applicable To**: B2B, SaaS, professional services

### AP-003: Choice Overload
- **Pattern**: More than 3 options presented simultaneously -> PFC overload -> decision paralysis
- **Brain Signature**: PFC saturates and then drops (paradoxical deactivation)
- **Effect Size**: -40% conversion when >3 options vs. 1-2 options
- **Confidence**: Medium-High (n=223)
- **Applicable To**: Pricing pages, product comparison content

---

## Pattern Validation Status
| Status | Count | Description |
|--------|-------|------------|
| Validated | 14 | Confirmed with sufficient data and cross-validation |
| Provisional | 4 | Emerging pattern, needs more data |
| Invalidated | 0 | Previously believed patterns disproven |
| Under Investigation | 3 | Data collection in progress |

## See Also
- [[Learner-Agent]] — Agent that discovers and validates these patterns
- [[Calibration-Log]] — Related calibration adjustments
- [[Optimizer-Agent]] — Uses these patterns for recommendations
- [[Content-Scoring-Framework]] — How patterns inform the scoring model
