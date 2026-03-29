---
title: Deployer Agent
type: agent
tags: [agent, deployer, publishing, distribution, scheduling]
related: [[Creative-Agent]], [[TRIBE-Scorer-Agent]], [[Optimizer-Agent]]
---

# Deployer Agent

## Purpose
Handles content publishing, distribution, and scheduling across platforms. Ensures optimized content reaches the right audience at the right time.

## What It Does
1. **Platform Formatting**: Adapts content to each platform's specifications (aspect ratio, duration, caption length)
2. **Scheduling**: Determines optimal posting times based on audience analytics
3. **Distribution**: Publishes content across configured platforms
4. **Asset Management**: Manages thumbnails, captions, hashtags, and metadata per platform
5. **Cross-Posting Adaptation**: Transforms long-form to short-form clips, adjusts for platform norms
6. **A/B Deployment**: Deploys test variants when [[Optimizer-Agent]] suggests A/B tests

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `content_package` | ContentPackage | Final content + all assets |
| `score_report` | ScoreReport | From [[TRIBE-Scorer-Agent]] |
| `platforms` | list[str] | Target platforms for distribution |
| `schedule` | Schedule | Publishing timeline (immediate or scheduled) |
| `ab_variants` | list[Variant] | Optional A/B test variants |
| `audience_segments` | list[Segment] | Target audience segments |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `deployment_log` | list[Deployment] | Record of each publication |
| `platform_urls` | dict | Published URLs per platform |
| `ab_test_ids` | list[str] | IDs for tracking A/B tests |
| `scheduled_posts` | list[ScheduledPost] | Upcoming scheduled publications |
| `performance_tracking` | dict | Initial metrics tracking setup |

## API Endpoints Used
- TikTok Publishing API
- YouTube Data API (upload + metadata)
- Instagram Graph API (publishing)
- LinkedIn Marketing API
- Twitter/X API v2
- Facebook Pages API
- Buffer/Hootsuite API (optional scheduling layer)
- URL shortener (for tracking links)

## Knowledge Vault Files Referenced
- [[Content-Scoring-Framework]] — Score thresholds for auto-publish vs. hold for review
- [[Hook-Science]] — Platform-specific hook formatting
- [[Attention-Curves]] — Content length optimization per platform

## Platform Specifications
| Platform | Max Duration | Aspect Ratio | Caption Limit | Hashtag Strategy |
|----------|-------------|-------------|--------------|-----------------|
| TikTok | 10 min | 9:16 | 2,200 chars | 3-5 relevant |
| Instagram Reels | 90s | 9:16 | 2,200 chars | 20-30 (mix niche + broad) |
| YouTube Shorts | 60s | 9:16 | 100 chars title | Tags in description |
| YouTube Long | 12h | 16:9 | 5,000 chars desc | Tags + chapters |
| LinkedIn | 10 min | 16:9 or 1:1 | 3,000 chars | 3-5 industry |
| Twitter/X | 2:20 | 16:9 | 280 chars | 1-2 max |

## Publishing Decision Tree
```
Content Ready for Deploy
    |
    v
[TRIBE Score > 70?]
    Yes -> Auto-publish approved
    No -> [Score > 50?]
            Yes -> Flag for human review
            No -> Send back to [[Optimizer-Agent]]
    |
    v
[A/B Test Requested?]
    Yes -> Deploy variants with tracking
    No -> Deploy single version
    |
    v
[Scheduled or Immediate?]
    Scheduled -> Queue with optimal timing
    Immediate -> Publish now
    |
    v
[Multi-Platform?]
    Yes -> Adapt and deploy per platform
    No -> Deploy to target platform
    |
    v
Set up performance tracking
Notify [[Learner-Agent]] to begin monitoring
```

## Optimal Posting Times
Determined by historical audience analytics, adjusted weekly:
| Platform | General Best Times | Notes |
|----------|-------------------|-------|
| TikTok | 7-9 AM, 12-1 PM, 7-11 PM | Weekdays slightly better |
| Instagram | 11 AM-1 PM, 7-9 PM | Tuesday-Thursday peak |
| YouTube | 2-4 PM (for recommendation algo) | Thursday-Saturday |
| LinkedIn | 7-8 AM, 12 PM, 5-6 PM | Tuesday-Thursday only |

> These are defaults. Agent learns audience-specific patterns via [[Learner-Agent]].

## Status Indicators
| Status | Meaning |
|--------|---------|
| `formatting` | Adapting content for platform specs |
| `scheduling` | Determining optimal post time |
| `publishing` | Actively uploading/posting |
| `published` | Content live, tracking setup |
| `ab_active` | A/B test running |
| `held` | Content below score threshold, awaiting review |
| `error` | Publishing API failure |

## Handoffs
- Receives final content from [[Creative-Agent]] (after [[Optimizer-Agent]] refinement)
- Performance data -> [[Learner-Agent]] (for analysis and pattern discovery)
- Deployment logs -> Dashboard (for team visibility)
- A/B test results -> [[Optimizer-Agent]] (for pattern validation)

## See Also
- [[Creative-Agent]] — Creates the content being deployed
- [[Optimizer-Agent]] — Ensures content meets quality threshold
- [[TRIBE-Scorer-Agent]] — Provides quality gate scoring
- [[Learner-Agent]] — Monitors post-deployment performance
