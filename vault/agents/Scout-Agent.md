---
title: Scout Agent
type: agent
tags: [agent, scout, discovery, competitor, monitoring]
related: [[Competitor-Analysis-Template]], [[Discovered-Patterns]], [[Learner-Agent]]
---

# Scout Agent

## Purpose
Discovers and monitors competitor content, trending topics, and high-performing content in target niches. The eyes and ears of the TRIBE system.

## What It Does
1. **Competitor Monitoring**: Tracks specified competitor accounts across platforms for new content
2. **Trend Detection**: Identifies emerging topics, formats, and hooks gaining traction
3. **Content Discovery**: Finds high-performing content in target categories for analysis
4. **Benchmark Collection**: Gathers performance metrics (views, engagement, shares) for calibration
5. **Signal Aggregation**: Compiles daily/weekly intelligence briefings

## Inputs
| Input | Type | Description |
|-------|------|------------|
| `competitor_accounts` | list[str] | Social media handles to monitor |
| `target_niches` | list[str] | Content categories to track |
| `platforms` | list[str] | Platforms to scan (TikTok, YouTube, Instagram, LinkedIn) |
| `lookback_hours` | int | How far back to search (default: 24) |
| `min_engagement` | int | Minimum engagement threshold to flag content |

## Outputs
| Output | Type | Description |
|--------|------|------------|
| `discovered_content` | list[ContentItem] | New content found with metadata |
| `trend_signals` | list[TrendSignal] | Emerging trends with confidence scores |
| `competitor_updates` | list[CompetitorUpdate] | Changes in competitor behavior |
| `intelligence_brief` | str | Summarized daily/weekly briefing |

## API Endpoints Used
- Platform APIs (TikTok, YouTube Data API, Instagram Graph API, LinkedIn API)
- Social listening tools (configured per deployment)
- RSS feeds for blog/publication monitoring
- Google Trends API for search trend validation

## Knowledge Vault Files Referenced
- [[Competitor-Analysis-Template]] — Template for structuring competitor findings
- [[Discovered-Patterns]] — Cross-references findings against known patterns
- [[Hook-Science]] — Identifies hook patterns in discovered content
- [[Attention-Curves]] — Classifies content by attention curve archetype

## Workflow
```
1. Scheduled trigger (hourly/daily)
2. Query platform APIs for new content from tracked accounts
3. Filter by engagement thresholds
4. Extract metadata: format, duration, topic, hook type
5. Flag content for [[TRIBE-Scorer-Agent]] analysis
6. Identify trend patterns across multiple content pieces
7. Generate intelligence brief
8. Store findings and update [[Discovered-Patterns]]
```

## Status Indicators
| Status | Meaning |
|--------|---------|
| `scanning` | Actively querying platforms |
| `processing` | Analyzing discovered content metadata |
| `briefing` | Generating intelligence summary |
| `idle` | Waiting for next scheduled run |
| `rate_limited` | API rate limit hit, waiting for reset |
| `error` | API failure or unexpected response |

## Configuration
```json
{
  "schedule": "0 */4 * * *",
  "max_items_per_scan": 100,
  "engagement_threshold": 1000,
  "trend_confidence_threshold": 0.7,
  "platforms": ["tiktok", "youtube", "instagram", "linkedin"],
  "alert_on_viral": true,
  "viral_threshold": 10000
}
```

## Handoffs
- Discovered content -> [[TRIBE-Scorer-Agent]] (for brain-based scoring)
- Trend signals -> [[Creative-Agent]] (for content ideation)
- Competitor updates -> [[Optimizer-Agent]] (for strategy adjustment)
- Intelligence briefs -> Dashboard / notification system

## See Also
- [[Creative-Agent]] — Receives trend signals for content creation
- [[TRIBE-Scorer-Agent]] — Scores discovered content
- [[Learner-Agent]] — Learns from Scout's discovery patterns
- [[Competitor-Analysis-Template]] — Template for competitor reports
