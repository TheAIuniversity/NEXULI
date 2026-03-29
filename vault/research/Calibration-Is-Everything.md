---
title: Calibration Is Everything
type: research
tags: [calibration, validation, business-critical, learner-agent]
related: [[Content-Scoring-Framework]], [[TRIBE-v2-Architecture]], [[Calibration-Log]]
---

# Calibration Is Everything

## The One Number That Determines If TRIBE Is A Business Or A Demo

The Pearson correlation (r) between TRIBE brain scores and real-world ad performance (CTR, conversion, watch time) is the single most important metric in this entire system.

- **r > 0.5** → TRIBE predictions are commercially defensible. We can sell this.
- **r = 0.3–0.5** → Weak signal. Useful as a directional tool, not reliable enough for autonomous decisions.
- **r < 0.3** → TRIBE brain scores do not predict real marketing outcomes. The product is a demo, not a tool.

## Why This Matters

TRIBE predicts how the **average human brain** responds to content. That is scientifically valid — Meta validated it against 720 real brains with 54% of explainable variance captured.

But predicting brain response is NOT the same as predicting business outcomes. A video can trigger massive prefrontal activation (brain says: "this is interesting") and still convert at 0.1% because the offer is wrong, the targeting is off, the price is too high, or the audience doesn't need the product.

The calibration study answers: **does brain activation actually predict what we care about — clicks, conversions, revenue?**

## What The Learner Agent Must Do

1. Collect paired data: every scored piece of content + its real-world performance after deployment
2. Require minimum 50 paired samples before computing any correlation
3. Compute Pearson r between each brain region score and each real metric
4. Store in `patterns/calibrated/` with scope="calibrated"
5. Update AgentBrain learning_weights ONLY from calibrated patterns
6. Report calibration readiness honestly — never fake accuracy numbers

## What Happens At Each Threshold

| r value | What it means | What we do |
|---|---|---|
| Not yet computed | < 50 paired samples | Keep scoring + deploying + collecting. Do not claim predictive power. |
| r < 0.3 | Brain scores don't predict performance | Investigate why. Maybe wrong regions. Maybe wrong metric. Maybe TRIBE just doesn't predict marketing. Be honest. |
| r = 0.3–0.5 | Weak but real signal | Use as ONE input alongside other signals. Don't automate decisions on this alone. |
| r > 0.5 | Strong predictive signal | We have a product. Start building the commercial model (Phase 8). |
| r > 0.7 | Exceptional | This would be world-class. Publish results. Raise prices. |

## The Honest Risk

Nobody has ever validated a brain encoding model against marketing metrics at scale. Meta validated TRIBE against brain data, not business data. We are the first to attempt this. It might not work. That is not a failure — it is a scientific finding. But we must know before we sell.
