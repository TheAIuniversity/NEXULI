# TRIBE Marketing Intelligence — Ongoing Progress

Last updated: 2026-03-28

---

## DONE

### Backend
- [x] FastAPI server with 13 endpoints (server.py)
- [x] TRIBE v2 engine wrapper with lazy loading (tribe_engine.py)
- [x] Brain → marketing score conversion pipeline (scoring.py)
- [x] SQLite storage with 5 tables (storage/db.py)
- [x] Configuration with env var support (config.py)
- [x] Requirements file

### Agents
- [x] Scorer Agent — scores content through TRIBE, persists results
- [x] Optimizer Agent — generates fix recommendations from scores
- [x] Learner Agent — discovers patterns across scored content
- [x] Scout Agent — tracks competitors (add/list)
- [x] Creative Agent — generates briefs from learned patterns
- [x] Deployer Agent — stub ready for integrations

### Intelligence Layer (stolen patterns, integrated)
- [x] Agent Brain — evolving JSON with adaptive learning weights, rolling benchmarks, modality insights, hook patterns (from goviralbitch)
- [x] Competitor Scraper — anti-bot headers, rotating UAs, tech stack fingerprinting (26 tools across 6 categories), tracker detection, CTA extraction (from Scrapling + Argus)
- [x] Knowledge Graph — temporal episodes with valid_at/created_at, entity upsert with dedup, edge invalidation when facts change, dual-level search (from Graphiti + LightRAG)
- [x] Token Compression — 5-level pipeline: whitespace → JSON compact → dictionary substitution (16 TRIBE abbreviations) → observation compression → truncation. 80% savings measured (from ClawRouter)
- [x] Engagement Normalization — platform-specific log1p formulas for Reddit, X, YouTube, LinkedIn, Instagram, TikTok with cross-platform 0-100 scoring (from goviralbitch)
- [x] Near-Duplicate Detection — trigram Jaccard similarity with length pre-filter, keeps highest-scored item per cluster (from goviralbitch)

### TRIBE v2 Deep Integration (10 critical fixes)
- [x] FIX 1: Real HCP-MMP1 atlas — 360 brain regions grouped into 12 marketing clusters, replaces fake REGION_MASKS (atlas.py)
- [x] FIX 2: Timestamp correction — 2Hz/0.5s per TR, not 1Hz/1s (atlas.py constants)
- [x] FIX 3: True modality ablation — zero each modality, measure real delta, no more brain-region proxy (ablation.py)
- [x] FIX 4: Content embeddings — extract 1152-dim fused + 2048-dim bottleneck vectors for similarity/clustering/recommendation (embeddings.py)
- [x] FIX 5: Audience archetypes — 25 subject heads mapped to 4 audience types (Visual Engager, Audio Learner, Sustained Viewer, Quick Scanner) with per-archetype scoring (audience.py)
- [x] FIX 6: Temporal dynamics — cross-second gradients, attention flow correlations, coherence score, momentum curve, critical transitions (temporal.py)
- [x] FIX 7: RGB brain overlay — text=R, audio=G, video=B per-vertex, shows all modality contributions on one brain (rgb_brain.py)
- [x] FIX 8: Segment event mapping — connects specific words/scenes/audio to their brain response, word-level impact ranking (segment_mapper.py)
- [x] FIX 9: Fine-tuning pipeline — config for training custom heads on engagement data, paired data collector with readiness report (finetune.py)
- [x] FIX 10: RGB visualization data ready for frontend BrainViewer (rgb_brain.py outputs feed directly into per-vertex coloring)

### Obsidian Knowledge Vault (27 files)
- [x] Research folder (5 files) — architecture, training, brain regions, inference, papers
- [x] Brain mapping folder (6 files) — one per region with marketing rules
- [x] Marketing folder (5 files) — scoring framework, modality analysis, hook science, attention curves, weak moments
- [x] Agents folder (6 files) — documentation per agent
- [x] Patterns folder (2 files) — 21 discovered patterns + calibration log
- [x] Templates folder (2 files) — score + competitor templates

### Orchestration Layer (stolen from 1st agentic system)
- [x] Autonomous Loop — infinite check→get→execute→validate cycle with LoopTask queue, configurable callbacks, pause/stop/resume (from /go command)
- [x] Strategist — reads system state, identifies gaps, generates prioritized tasks: score→optimize→scout→learn→calibrate (from strategist.md)
- [x] Campaign Coordinator — 8-state machine (DRAFT→SCORING→OPTIMIZING→RESCORING→REVIEW→APPROVED→DEPLOYED→COMPLETED) with human review gate (from coordinator.md)
- [x] Goal Tracker — JSON-persisted goals with per-criterion tracking, progress %, GOAL_COMPLETE detection (from goal.md)
- [x] Block Resolver — classifies errors into 6 block types (knowledge, capability, data, error, permission, resource) with resolution strategies (from meta-skill.md)
- [x] Model Router — task-type-first routing to haiku/sonnet/opus with keyword fallback + cost estimation (from model-router.md)

### Frontend Dashboard
- [x] JARVIS dark theme, 7 tabs, 1,550 lines
- [x] Command tab (3-column ops view)
- [x] Scanner tab (upload + attention curve + brain regions + modality + moments + score circle)
- [x] Creative tab (4 variant comparison cards)
- [x] Scout tab (competitor cards + benchmarks)
- [x] Agents tab (6 agent status cards)
- [x] Learning tab (patterns + calibration + stats)
- [x] Chat tab (full chat interface)

---

## IN PROGRESS

### Hardware
- [ ] **Buy Mac Mini M4** (16 GB+ RAM required for TRIBE inference)
  - M4 with 16 GB minimum, 24 GB recommended
  - Will serve as dedicated TRIBE inference server
  - Also runs the backend API + agents 24/7

---

## TODO — Next Steps (Priority Order)

### Phase 1: Get TRIBE v2 Running (needs Mac Mini)
- [ ] Install TRIBE v2 on Mac Mini (`pip install tribev2`)
- [ ] Download all backbone models (~15 GB): LLaMA 3.2-3B, V-JEPA2, Wav2Vec-BERT, DINOv2
- [ ] Accept LLaMA 3.2 license on HuggingFace (gated model, needs approval)
- [ ] Run first test score on a sample video
- [ ] Measure actual inference speed on M4 hardware
- [ ] Verify GPU memory usage (MPS backend on Apple Silicon)

### Phase 2: TRIBE v2 Calibration — Make The Scores Accurate
- [ ] Validate REGION_MASKS in scoring.py against actual fsaverage5 atlas
  - Current vertex ranges are approximate estimates
  - Need to load actual fsaverage5 mesh and map Desikan-Killiany atlas labels to vertex indices
  - This determines accuracy of ALL marketing scores
- [ ] Score 10+ known content pieces (ads that performed well vs poorly)
- [ ] Compare TRIBE brain region activations against what we'd expect
- [ ] Adjust region weights in attention formula based on real results
- [ ] Tune the weak/peak moment detection thresholds
- [ ] Validate modality contribution percentages make sense

### Phase 3: Connect Frontend to TRIBE v2 Backend
- [ ] Move dashboard.tsx into the Next.js app properly (currently at /marketing)
- [ ] Replace all mock data in dashboard with real TRIBE API calls to localhost:8100
- [ ] Wire up Scanner tab upload → POST /api/score → display real TRIBE brain maps
- [ ] Wire up Agents tab to GET /api/agents
- [ ] Wire up Learning tab to GET /api/patterns
- [ ] Wire up Scout tab to GET /api/competitors
- [ ] Wire up Chat tab to a chat endpoint (needs building)
- [ ] Wire up activity feed to GET /api/feed
- [ ] Add real-time polling (30s intervals) for agent statuses

### Phase 4: TRIBE v2 + Agents — Wire Agents to Real TRIBE Scoring
- [ ] **Scout Agent** — score competitor content through TRIBE
  - Integrate Meta Ad Library API (public, free)
  - Scrape competitor landing pages + video ads
  - Auto-score ALL competitor content through TRIBE v2
  - Compare competitor TRIBE scores against your scores
  - Store results + update brain benchmarks
- [ ] **Creative Agent** — use TRIBE patterns to generate briefs
  - Use Claude API to generate creative briefs
  - Feed TRIBE-derived brain region rules as constraints ("prefrontal must spike at CTA")
  - Reference vault brain-mapping files for specific guidance per region
  - Generate variants designed to score high on TRIBE
- [ ] **Optimizer Agent** — TRIBE-specific fix recommendations
  - Map each TRIBE brain region drop to specific creative fixes
  - "Visual cortex flat at 0:12 → add scene change"
  - "Prefrontal drop at 0:22 → CTA too early, move to 0:28"
  - "Fusiform face area low → add human face"
  - Priority scoring based on which brain region has highest learning weight in the brain
- [ ] **Deployer Agent** — ad platform integrations
  - Meta Ads API integration (create/update campaigns)
  - Google Ads API integration
  - TikTok Ads API integration
  - Auto-deploy TRIBE-approved variants (score above target)
- [ ] **Learner Agent** — calibrate TRIBE against real-world outcomes
  - Pull actual performance data from ad platforms (CTR, conversion, CPA, watch time)
  - Pair with TRIBE brain scores for every deployed content piece
  - Calculate correlation per brain region: "visual cortex score correlates 0.72 with watch time"
  - Update brain learning_weights based on which regions actually predict performance
  - Discover new patterns: "content with prefrontal spike at second 3 converts 2.1x better"
  - Write patterns to vault/patterns/Discovered-Patterns.md
  - This is the core feedback loop that makes TRIBE smarter over time

### Phase 5: TRIBE v2 Autonomous Loop — Continuous Scoring + Optimization
- [ ] Wire the autonomous loop (orchestration/loop.py) to real TRIBE scoring
- [ ] Strategist auto-generates tasks: "5 unscored files → create scoring tasks"
- [ ] Loop: score content → find weak spots → optimizer generates fixes → re-score → loop until target
- [ ] Campaign coordinator moves campaigns through states automatically
- [ ] Goal tracker checks: "all content above 80?" → GOAL_COMPLETE → stop loop
- [ ] Block resolver handles TRIBE failures (out of memory → try smaller batch, model not loaded → load it)

### Phase 6: Chat Interface — Talk to TRIBE
- [ ] Build chat API endpoint (POST /api/chat)
- [ ] Connect to Claude API for natural language interaction
- [ ] System prompt includes vault knowledge + TRIBE capabilities
- [ ] User asks "Score this video" → triggers TRIBE v2 → returns brain map + scores in natural language
- [ ] User asks "Compare these two ads" → runs both through TRIBE → shows side-by-side brain activation
- [ ] User asks "What's our best hook pattern?" → queries brain + knowledge graph → returns data-backed answer
- [ ] User asks "Why did this ad fail?" → loads TRIBE score → explains which brain regions dropped and why

### Phase 7: TRIBE v2 Intermediate Representations — Content Embeddings
- [ ] Modify tribe_engine.py to extract intermediate transformer representations
  - After feature aggregation: (batch, timesteps, 1152) — raw multimodal fusion
  - After transformer: (batch, timesteps, 1152) — fully fused cross-modal representation
  - After low-rank head: (batch, timesteps, 2048) — brain-optimized bottleneck
- [ ] The 2048-dim bottleneck is a per-second content embedding optimized for predicting human response
- [ ] Use these embeddings for:
  - Content similarity search (cosine distance — "find ads similar to this one")
  - Content clustering (discover natural content categories)
  - Content recommendation ("your best-performing content is similar to these competitor pieces")
  - Audience matching ("content with this embedding profile converts for segment X")
- [ ] Build vector store for TRIBE content embeddings

### Phase 8: TRIBE v2 Custom Training — Your Own Model
- [ ] Collect paired data: TRIBE brain scores + real campaign performance (from Phase 4 learner)
- [ ] Train custom prediction heads on top of TRIBE's 2048-dim bottleneck
  - Target: CTR prediction per audience segment
  - Target: conversion rate prediction
  - Target: watch time prediction
- [ ] Per-audience-segment heads (same architecture as TRIBE's per-subject heads)
  - Replace 25 brain subjects with N audience segments
  - Same architecture, different training target
  - Now you're predicting "how does THIS audience respond" not "how does the average brain respond"
- [ ] This creates a commercially licensable model (own weights, own training data)
- [ ] The more content you score + deploy + measure, the better this model gets

### Phase 9: Production Deployment
- [ ] Dockerize the backend (TRIBE v2 + all agents + intelligence layer + orchestration)
- [ ] Set up the Mac Mini as a dedicated TRIBE inference server
  - Static IP or Tailscale for remote access
  - PM2 or systemd for process management
  - Auto-restart on crash
  - TRIBE model stays loaded in memory 24/7
- [ ] Connect dashboard to production backend URL
- [ ] Deploy frontend to the main AI University site or separate domain
- [ ] SSL/HTTPS for the API
- [ ] Authentication for the dashboard
- [ ] Rate limiting on the scoring endpoint
- [ ] Monitoring: TRIBE inference speed, GPU usage, scoring queue depth

---

## KNOWN ISSUES

- **REGION_MASKS are approximate** — vertex ranges in scoring.py are estimated, not verified against the actual fsaverage5 atlas. This is the biggest accuracy risk. Needs validation in Phase 3.
- **No GPU on current droplet** — DigitalOcean droplet has 2 vCPU / 2 GB RAM, no GPU. Cannot run TRIBE. Mac Mini required.
- **LLaMA 3.2 is gated** — needs HuggingFace account approval before TRIBE can use the text encoder. Apply at https://huggingface.co/meta-llama/Llama-3.2-3B
- **WhisperX dependency** — TRIBE uses `uvx whisperx` for transcription. Needs UV package manager installed.
- **CC BY-NC license on TRIBE weights** — pre-trained model is non-commercial. Architecture patterns and frozen encoders (V-JEPA2, Wav2Vec-BERT) are commercially licensed. For commercial product: train own fusion weights on own data (Phase 7).

---

## IDEAS / FUTURE

- [ ] Real-time video scoring (stream frames through TRIBE as video plays)
- [ ] Browser extension that scores any video on the web
- [ ] Obsidian plugin that auto-updates patterns from the learner agent
- [ ] A/B test predictor — score 1000 variants, pick top 5, deploy
- [ ] ICA decomposition on transformer representations to discover hidden audience segments
- [ ] Integrate with AI University agent system (TRIBE as an MCP tool)
- [ ] White-label the dashboard for agencies
- [ ] Content benchmark database across industries (the long-term moat)
