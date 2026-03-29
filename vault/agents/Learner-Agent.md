---
title: Learner Agent
type: agent
tags: [agent, learner, patterns, calibration, feedback, ml]
related: [[Discovered-Patterns]], [[Calibration-Log]], [[TRIBE-Scorer-Agent]]
---

# Learner Agent

## Purpose
Closes the feedback loop. Monitors deployed content performance, correlates with TRIBE predictions, discovers new patterns, and calibrates the scoring model.

## What It Does
1. **Performance Monitoring**: Tracks real-world metrics (views, retention, CTR, conversions) for deployed content
2. **Prediction Validation**: Compares TRIBE brain scores against actual platform performance
3. **Pattern Discovery**: Identifies new correlations between brain activation patterns and outcomes
4. **Score Calibration**: Adjusts scoring weights when TRIBE predictions drift from reality
5. **A/B Analysis**: Analyzes A/B test results to validate or invalidate optimization hypotheses
6. **Knowledge Update**: Updates [[Discovered-Patterns]] and [[Calibration-Log]] with new findings

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `deployment_log` | list[Deployment] | From [[Deployer-Agent]] |
| `score_reports` | list[ScoreReport] | Original TRIBE scores |
| `platform_metrics` | dict | Real-world performance data |
| `ab_test_results` | list[ABResult] | A/B test outcomes |
| `time_window` | str | Analysis period (daily, weekly, monthly) |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `new_patterns` | list[Pattern] | Newly discovered correlations |
| `calibration_updates` | list[CalibrationUpdate] | Score weight adjustments |
| `prediction_accuracy` | dict | How well TRIBE predicted outcomes |
| `pattern_validations` | list[Validation] | Existing patterns confirmed/invalidated |
| `learning_report` | str | Summary of findings and recommendations |

## API Endpoints Used
- Platform analytics APIs (TikTok Analytics, YouTube Analytics, Instagram Insights, LinkedIn Analytics)
- Internal metrics database
- [[TRIBE-Scorer-Agent]] API (for re-scoring with updated weights)

## Knowledge Vault Files Referenced
- [[Discovered-Patterns]] — Pattern library to update
- [[Calibration-Log]] — Calibration history to maintain
- [[Content-Scoring-Framework]] — Scoring weights to adjust
- All brain region files for correlation analysis

## Learning Loop
```
1. Collect performance metrics for deployed content (24h, 7d, 30d windows)
2. Match performance data to original TRIBE score reports
3. Compute prediction accuracy:
   - Correlation between TRIBE overall score and engagement rate
   - Correlation between hook score and retention at 3 seconds
   - Correlation between weak moment count and drop-off points
4. Identify discrepancies:
   - High TRIBE score + low performance = scoring overestimates
   - Low TRIBE score + high performance = scoring underestimates
5. Analyze discrepancy patterns:
   - Consistent by brain region? -> Adjust region weight
   - Consistent by platform? -> Add platform-specific calibration
   - Consistent by content type? -> Add content-type calibration
6. Update [[Discovered-Patterns]] with new findings
7. Update [[Calibration-Log]] with adjustments
8. Notify team of significant findings
```

## Pattern Discovery Process
```
For each content piece with performance data:
  1. Extract brain activation features (per-region, temporal, cross-modal)
  2. Extract performance metrics (views, retention curve, CTR, conversions)
  3. Compute correlations between brain features and performance
  4. Flag correlations with |r| > 0.3 and p < 0.05 as candidate patterns
  5. Cross-validate against historical data
  6. If validated: add to [[Discovered-Patterns]] with confidence score
  7. If invalidated: flag as spurious, do not add
```

## Calibration Methodology
Score calibration uses a rolling window approach:
- **Window**: Last 100 scored + deployed content pieces
- **Method**: Linear regression of TRIBE scores against normalized performance
- **Adjustment**: Scale and offset per brain region weight
- **Frequency**: Weekly recalibration, monthly deep review
- **Guard rails**: No single region weight changes by more than 5% per calibration cycle

## Prediction Accuracy Targets
| Metric | TRIBE Predictor | Target Correlation |
|--------|----------------|-------------------|
| Retention at 3s | Hook score | r > 0.5 |
| Avg view duration | Overall score | r > 0.4 |
| Engagement rate | Overall score | r > 0.35 |
| CTR (thumbnail) | FFA score | r > 0.4 |
| Conversion rate | PFC score at CTA | r > 0.3 |
| Share rate | DMN peak score | r > 0.25 |

## Status Indicators
| Status | Meaning |
|--------|---------|
| `collecting` | Gathering performance metrics |
| `correlating` | Computing TRIBE vs. performance correlations |
| `discovering` | Running pattern discovery analysis |
| `calibrating` | Adjusting score weights |
| `reporting` | Generating learning report |
| `idle` | Waiting for next analysis window |

## Handoffs
- Performance data from [[Deployer-Agent]]
- Calibration updates -> [[TRIBE-Scorer-Agent]] (adjusted weights)
- New patterns -> [[Discovered-Patterns]] (knowledge base)
- Calibration history -> [[Calibration-Log]] (audit trail)
- Validated patterns -> [[Optimizer-Agent]] (for better recommendations)
- Learning reports -> Dashboard / team notification

## See Also
- [[Discovered-Patterns]] — Living pattern library this agent maintains
- [[Calibration-Log]] — Calibration audit trail
- [[TRIBE-Scorer-Agent]] — Scoring model this agent calibrates
- [[Optimizer-Agent]] — Uses validated patterns for recommendations
- [[Deployer-Agent]] — Source of performance data
