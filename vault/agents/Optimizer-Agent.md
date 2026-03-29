---
title: Optimizer Agent
type: agent
tags: [agent, optimizer, recommendations, improvement, iteration]
related: [[Content-Scoring-Framework]], [[Weak-Moment-Patterns]], [[TRIBE-Scorer-Agent]]
---

# Optimizer Agent

## Purpose
Takes TRIBE score reports and generates specific, actionable optimization recommendations. Turns brain data into creative direction.

## What It Does
1. **Score Interpretation**: Analyzes [[TRIBE-Scorer-Agent]] output to identify improvement areas
2. **Weak Moment Diagnosis**: Maps weak moments to root causes using [[Weak-Moment-Patterns]]
3. **Fix Recommendation**: Generates specific, timestamped fixes for each issue
4. **Priority Ranking**: Orders recommendations by expected impact
5. **A/B Suggestion**: Proposes testable variations for uncertain fixes
6. **Re-Score Prediction**: Estimates score improvement for each recommendation

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `score_report` | ScoreReport | Full output from [[TRIBE-Scorer-Agent]] |
| `content_metadata` | dict | Platform, audience, goals, constraints |
| `brand_guidelines` | BrandGuidelines | Voice, visual, and audio constraints |
| `optimization_target` | str | What to optimize: "hook", "retention", "conversion", "overall" |
| `effort_budget` | str | "quick-fix", "moderate", "full-rework" |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `recommendations` | list[Recommendation] | Prioritized optimization recommendations |
| `estimated_score_improvement` | float | Predicted score increase if all applied |
| `quick_wins` | list[Recommendation] | Changes achievable in <30 minutes |
| `structural_changes` | list[Recommendation] | Larger changes requiring re-edit or re-shoot |
| `ab_test_suggestions` | list[ABTest] | Proposed A/B tests for uncertain optimizations |

## Recommendation Format
```json
{
  "id": "opt-001",
  "priority": 1,
  "type": "weak_moment_fix",
  "timestamp": "22s-28s",
  "brain_region": "visual_cortex",
  "current_score": 32,
  "predicted_score": 58,
  "effort": "quick-fix",
  "recommendation": "Replace static talking head at 22-28s with B-roll showing the product in use. Current visual cortex activation is flat (32) due to no scene changes for 6 seconds.",
  "rationale": "Visual cortex flatlines after 4-5 seconds of the same frame. Scene change will spike V1/V2 activation. Pattern validated in [[Discovered-Patterns]].",
  "alternatives": [
    "Add zoom/pan on existing footage (less effective, easier)",
    "Add text overlay with motion graphics (moderate effectiveness)"
  ]
}
```

## API Endpoints Used
- [[TRIBE-Scorer-Agent]] API (for re-scoring predictions)
- Pattern database (stored [[Discovered-Patterns]])
- LLM API for natural language recommendation generation

## Knowledge Vault Files Referenced
- [[Content-Scoring-Framework]] — Understanding what drives scores
- [[Weak-Moment-Patterns]] — Root cause analysis templates
- [[Attention-Curves]] — Optimal curve shapes to target
- [[Hook-Science]] — Hook optimization if hook score is low
- [[Visual-Cortex]], [[Auditory-Cortex]], [[Language-Areas]], [[Prefrontal-Cortex]], [[Default-Mode-Network]], [[Fusiform-Face-Area]] — Region-specific optimization rules
- [[Discovered-Patterns]] — Validated patterns to apply
- [[Modality-Analysis]] — Modality balance optimization

## Optimization Decision Tree
```
Score Report Received
    |
    v
[Hook Score < 50?]
    Yes -> Apply [[Hook-Science]] fixes (Priority 1)
    No -> Continue
    |
    v
[Weak Moments Detected?]
    Yes -> Classify by [[Weak-Moment-Patterns]]
           Fix severe first, then moderate, then mild
    No -> Continue
    |
    v
[Modality Imbalance?]
    Yes -> Apply [[Modality-Analysis]] rebalancing
    No -> Continue
    |
    v
[PFC Low at CTA?]
    Yes -> Apply [[Prefrontal-Cortex]] CTA optimization
    No -> Continue
    |
    v
[DMN Low Throughout?]
    Yes -> Apply [[Default-Mode-Network]] emotional hooks
    No -> Continue
    |
    v
[Coherence < 0.5?]
    Yes -> Address modality mismatch
    No -> Fine-tuning recommendations
```

## Effort Budgets

### Quick-Fix (< 30 minutes)
- Re-edit existing footage (cut/rearrange)
- Add text overlays or graphics
- Adjust audio levels
- Change thumbnail
- Modify caption/description

### Moderate (1-3 hours)
- Add B-roll footage
- Re-record voiceover sections
- Create motion graphics
- Shoot new hook
- Add sound design

### Full Rework (1+ days)
- Re-script entire piece
- Re-shoot with new structure
- New creative direction
- Complete audio redesign

## Status Indicators
| Status | Meaning |
|--------|---------|
| `analyzing` | Processing score report |
| `diagnosing` | Identifying root causes |
| `recommending` | Generating optimization suggestions |
| `estimating` | Predicting score improvements |
| `complete` | Recommendations ready |

## Handoffs
- Receives score reports from [[TRIBE-Scorer-Agent]]
- Recommendations -> [[Creative-Agent]] (for implementation)
- A/B test results -> [[Learner-Agent]] (for pattern validation)
- Validated fixes -> [[Discovered-Patterns]] (for pattern library)

## See Also
- [[TRIBE-Scorer-Agent]] — Provides input score reports
- [[Creative-Agent]] — Implements optimization recommendations
- [[Learner-Agent]] — Validates optimization effectiveness
- [[Weak-Moment-Patterns]] — Core diagnostic reference
- [[Attention-Curves]] — Target curve shapes
