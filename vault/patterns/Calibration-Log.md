---
title: Calibration Log
type: log
tags: [calibration, drift, weights, accuracy, tracking]
related: [[Discovered-Patterns]], [[Learner-Agent]], [[Content-Scoring-Framework]]
---

# Calibration Log

> **Audit trail of all scoring model calibrations.** Maintained by [[Learner-Agent]]. Each entry documents what changed, why, and the measured impact.

## Current Scoring Weights
As of 2026-03-28:

| Region | Weight | Last Adjusted | Reason |
|--------|--------|--------------|--------|
| Visual Cortex | 25% | 2026-03-15 | Baseline (no change) |
| Auditory Cortex | 20% | 2026-03-15 | Baseline (no change) |
| Language Areas | 20% | 2026-03-15 | Baseline (no change) |
| Prefrontal Cortex | 20% | 2026-03-15 | Baseline (no change) |
| Default Mode Network | 15% | 2026-03-15 | Baseline (no change) |

## Calibration History

### CAL-001: Initial Calibration (2026-03-15)
- **Type**: Full calibration
- **Dataset**: Initial reference set (n=500)
- **Changes**: Established baseline weights from TRIBE paper recommendations
- **Weights Set**: Visual 25%, Auditory 20%, Language 20%, PFC 20%, DMN 15%
- **Prediction Accuracy**:
  - Overall score vs. engagement: r=0.38
  - Hook score vs. 3s retention: r=0.45
  - FFA score vs. CTR: r=0.42
- **Notes**: Initial calibration. Weights derived from TRIBE v2 paper's regional predictability rankings. Higher-predictability regions weighted more.

### CAL-002: Platform-Specific Offset (2026-03-22)
- **Type**: Offset calibration
- **Dataset**: Platform-specific data (n=200 per platform)
- **Changes**: Added platform-specific score offsets
- **Offsets Added**:
  - TikTok: +3 (shorter content scores slightly lower by default)
  - YouTube: 0 (reference platform)
  - LinkedIn: +5 (text-heavy content naturally scores lower on visual/audio)
  - Instagram: +2 (image-based content missing audio component)
- **Prediction Accuracy Post-Calibration**:
  - TikTok engagement correlation: r=0.41 (up from 0.35)
  - LinkedIn engagement correlation: r=0.36 (up from 0.28)
- **Notes**: Platform offsets account for structural differences in content format. A LinkedIn text post should not be penalized for having zero audio activation.

## Calibration Methodology

### Triggers for Recalibration
1. **Scheduled**: Weekly automatic check, monthly deep review
2. **Drift detected**: When rolling 7-day prediction accuracy drops below threshold
3. **New pattern**: When [[Learner-Agent]] discovers a pattern that changes weight assumptions
4. **Manual**: When team identifies systematic scoring errors

### Drift Detection Thresholds
| Metric | Acceptable Range | Warning | Recalibration Required |
|--------|-----------------|---------|----------------------|
| Overall score vs. engagement | r > 0.30 | r = 0.25-0.30 | r < 0.25 |
| Hook score vs. 3s retention | r > 0.35 | r = 0.30-0.35 | r < 0.30 |
| FFA score vs. CTR | r > 0.30 | r = 0.25-0.30 | r < 0.25 |
| PFC at CTA vs. conversion | r > 0.20 | r = 0.15-0.20 | r < 0.15 |

### Guard Rails
- No single region weight changes by more than 5% per calibration cycle
- Total weights must sum to 100%
- Minimum weight for any region: 5%
- Maximum weight for any region: 40%
- Offsets cannot exceed +/- 15 points

### Calibration Process
```
1. Collect performance data for last 100 scored + deployed content pieces
2. Compute current prediction accuracy (per-metric Pearson correlation)
3. Compare against thresholds
4. If recalibration needed:
   a. Run linear regression: performance = f(region_scores)
   b. Extract optimal weights from regression coefficients
   c. Apply guard rails (max 5% change per region)
   d. Compute new prediction accuracy
   e. If improved: apply new weights
   f. If not improved: keep current weights, flag for investigation
5. Log all changes and rationale
6. Notify team of calibration results
```

## Accuracy Tracking Over Time
```
Date        | Overall r | Hook r | FFA-CTR r | Notes
------------|-----------|--------|-----------|------
2026-03-15  | 0.38      | 0.45   | 0.42      | Initial calibration
2026-03-22  | 0.41      | 0.46   | 0.43      | Platform offsets added
2026-03-28  | -         | -      | -         | Pending (data collection)
```

## Known Limitations
1. **Small sample**: Early calibration based on limited data. Confidence intervals are wide.
2. **Platform API lag**: Some platform metrics take 24-72 hours to stabilize (YouTube views especially)
3. **Confounding variables**: TRIBE score is not the only factor in performance. Posting time, audience size, hashtags, and platform algorithm changes all affect outcomes.
4. **Content type bias**: Current calibration skewed toward short-form video. Long-form and static content underrepresented.

## Future Calibration Plans
- [ ] Content-type-specific weights (video, static, audio, text)
- [ ] Industry-specific calibration (B2B vs. B2C vs. entertainment)
- [ ] Audience-size-adjusted scoring (viral potential vs. niche engagement)
- [ ] Seasonal adjustment (engagement patterns vary by season)

## See Also
- [[Discovered-Patterns]] — Patterns that may trigger recalibration
- [[Learner-Agent]] — Agent responsible for calibration
- [[Content-Scoring-Framework]] — The scoring system being calibrated
- [[TRIBE-Scorer-Agent]] — Agent that applies calibrated weights
