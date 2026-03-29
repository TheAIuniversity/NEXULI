# TRIBE API Endpoints & Pipelines

> Server: FastAPI on port 8100
> Start: `cd backend && python server.py`
> Docs: `http://localhost:8100/docs` (Swagger UI)

---

## All Endpoints

### Scoring

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| POST | `/api/score` | Score own content through TRIBE | `file` (multipart upload) | `{score, recommendations}` |
| POST | `/api/score/competitor` | Score competitor content | `file` + `competitor_name` (query) | `{score, source: "competitor"}` |
| GET | `/api/scores` | Score history | `limit` (query, default 50) | `[{filename, score, ...}]` |
| POST | `/api/tribe/load` | Explicitly preload TRIBE model | — | `{status: "loaded"}` |

### Agents

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/api/agents` | All agent statuses | — | `{agent_name: {status, metrics}}` |
| GET | `/api/agents/{name}/logs` | Agent activity logs | `limit` (query) | `[{agent, action, detail, created_at}]` |
| GET | `/api/feed` | Activity feed (all agents) | `limit` (query) | `[{agent, action, detail, created_at}]` |

### Pattern Vault

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/api/vault/stats` | Vault statistics | — | `{examples: {total, by_source, calibrated}, patterns, playbooks}` |
| GET | `/api/vault/patterns` | Discovered patterns | `scope`, `status`, `category` (queries) | `[{id, pattern, scope, confidence, ...}]` |
| GET | `/api/vault/playbooks` | Generated playbooks | — | `[{name, rules, scope}]` |
| GET | `/api/vault/examples` | Scored examples | `source`, `classification`, `limit` (queries) | `[{filename, source, score, ...}]` |
| POST | `/api/vault/analyze` | Trigger full pattern analysis | — | `{universal, competitor, calibrated, total_patterns}` |
| GET | `/api/vault/guidelines` | Creative guidelines | `scope` (query) | `{status, guidelines, based_on}` |
| GET | `/api/vault/calibration` | Calibration status | — | `{own_total, calibrated_samples, readiness_pct, status}` |

### Leads

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| POST | `/api/leads/classify` | Classify a lead by brain type | `lead_id` (query) + `interactions` (JSON body) | `{profile, actions}` |
| GET | `/api/leads/content-map` | Content brain map stats | — | `{total_pages_scored, by_type, by_funnel}` |

### Learning

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| POST | `/api/learn` | Trigger learning + calibration | — | `{analysis, calibration}` |

### Competitors

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/api/competitors` | List tracked competitors | — | `[{name, url, status, avg_score}]` |
| POST | `/api/competitors` | Add a competitor | `name`, `url` (queries) | `{status: "added"}` |

### Creative

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| POST | `/api/brief` | Generate creative brief | `content_type`, `target_score` (queries) | `{guidelines, structure}` |

### System

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/api/health` | System + model status | — | `{status, tribe_loaded, agents}` |

---

## Pipelines

### Pipeline 1: Score Own Content (End-to-End)

```
User uploads video to POST /api/score
        │
        ▼
server.py saves file with UUID prefix to uploads/
        │
        ▼
ScorerAgent.score(file_path)
        │
        ├── TribeEngine.predict(file_path)
        │   ├── Auto-detect modality (video/audio/text)
        │   ├── Run frozen encoders (LLaMA, V-JEPA2, Wav2Vec-BERT, DINOv2)
        │   ├── Run fusion transformer (8 layers, 1152 dim)
        │   └── Return predictions (n_trs, 20484) at 2Hz
        │
        ├── score_content(predictions, segments)
        │   ├── Map vertices to brain regions via HCP atlas
        │   ├── Compute per-region scores (12 marketing regions)
        │   ├── Normalize to 0-100
        │   ├── Compute attention = weighted sum of regions
        │   ├── Detect weak moments (attention < 40 for 2+ TRs)
        │   ├── Detect peak moments (attention > 80 for 2+ TRs)
        │   ├── Compute hook score (first 3 seconds)
        │   ├── Compute modality contribution (visual/audio/text %)
        │   └── Return ContentScore
        │
        ├── save_score() → tribe.db
        │
        └── vault.record_score(source="own") → vault.db
                ├── Auto-classify: GOOD (75+) / BAD (≤45) / NEUTRAL
                └── Stored with source="own"
        │
        ▼
OptimizerAgent.optimize(score_result)
        ├── Check hook score
        ├── Check weak moments
        ├── Check modality balance
        └── Generate fix recommendations
        │
        ▼
AgentBrain.update_from_score()
        ├── Update rolling averages
        ├── Update modality insights
        └── Save to brain.json
        │
        ▼
Return {score, recommendations} to user
        │
        ▼
Upload file deleted from disk
```

### Pipeline 2: Score Competitor Content

```
User uploads to POST /api/score/competitor?competitor_name=X
        │
        ▼
Same scoring pipeline as Pipeline 1
        │
        ▼
vault.record_score(source="competitor")
        ├── Stored separately from own content
        ├── NEVER used for calibration
        ├── NEVER updates learning weights
        └── Used for benchmarking only
        │
        ▼
Return {score, source: "competitor"}
```

### Pipeline 3: Pattern Learning

```
POST /api/vault/analyze (or POST /api/learn)
        │
        ▼
PatternVault.run_analysis()
        │
        ├── Pass 1: UNIVERSAL patterns
        │   ├── Load ALL examples (own + competitor)
        │   ├── Split by classification (GOOD vs BAD)
        │   ├── PatternExtractor compares metrics
        │   │   ├── Hook patterns (good vs bad hook scores)
        │   │   ├── Modality patterns (visual/audio/text distribution)
        │   │   ├── Region patterns (per brain region activation)
        │   │   ├── Structure patterns (weak/peak moment counts)
        │   │   └── Timing patterns (attention front-loading ratio)
        │   └── Patterns tagged scope="universal"
        │
        ├── Pass 2: COMPETITOR benchmarks
        │   ├── Load ONLY competitor examples
        │   ├── Compute averages, trends
        │   └── Patterns tagged scope="competitor"
        │
        └── Pass 3: CALIBRATED patterns (own data + real metrics)
            ├── Load ONLY own examples WITH real metrics (CTR, conversion, etc.)
            ├── Requires ≥5 samples per metric
            ├── Compute Pearson r between TRIBE scores and real performance
            ├── Example: "prefrontal > 70 correlates 0.82 with CTR > 2%"
            └── Patterns tagged scope="calibrated"
        │
        ▼
PlaybookGenerator.generate_all()
        ├── Universal playbooks (Hook Rules, Brain Activation Rules, etc.)
        ├── Competitor playbooks (Market Benchmark, Competitor Gaps)
        └── Calibrated playbook (Niche Playbook — YOUR data only)
        │
        ▼
Save to patterns.json + playbooks.json
```

### Pipeline 4: Lead Classification

```
POST /api/leads/classify
Body: {lead_id: "abc", interactions: [{url, timestamp, duration_seconds, scroll_depth, clicked_cta}]}
        │
        ▼
LeadClassifier.classify(lead_id, interactions)
        │
        ├── For each page visited:
        │   ├── Look up PageBrainProfile from content_map.db
        │   ├── Compute engagement weight (log duration × scroll × CTA boost)
        │   └── Accumulate weighted brain region scores
        │
        ├── Compute brain fingerprint (weighted average across all pages)
        │
        ├── Classify brain type:
        │   ├── Score each type against dominant regions
        │   ├── Decision Maker: decision + reward + action regions
        │   ├── Emotional Connector: emotion + social + memory regions
        │   ├── Visual Scanner: visual + face + attention regions
        │   ├── Audio Processor: auditory + language regions
        │   ├── Researcher: weighted by page count + diversity
        │   └── CTA click → 1.5x boost for Decision Maker
        │
        ├── Compute TRIBE lead score (0-100)
        │   ├── Mean of region scores
        │   ├── × 1.3 if visited decision-stage content
        │   └── × 1.5 if clicked CTA
        │
        └── Return LeadProfile
        │
        ▼
HyperTargeter.generate_actions(profile)
        ├── Decision Maker → sales call (critical) + case study (high)
        ├── Emotional Connector → testimonial (high) + community invite (medium)
        ├── Visual Scanner → retarget video ad (high) + visual email (medium)
        ├── Audio Processor → podcast link (high) + discovery call (medium)
        └── Researcher → complete guide (high) + honest comparison (medium)
        │
        ▼
Return {profile, actions}
```

### Pipeline 5: Calibration (Brain Weight Updates)

```
Triggered by: POST /api/vault/analyze (when ≥20 calibrated samples exist)
        │
        ▼
PatternVault.update_brain_weights()
        │
        ├── Guard: only uses scope="calibrated" + category="calibration" patterns
        ├── Guard: refuses if < 20 calibrated samples
        ├── Guard: NEVER touches competitor or universal data
        │
        ├── For each calibration pattern:
        │   ├── Read Pearson r between brain region and real metric
        │   ├── Weight by sample count (more data = more influence)
        │   └── Compute weighted average r per region
        │
        ├── Update AgentBrain.learning_weights:
        │   ├── If r > 0: increase weight (this region predicts performance)
        │   ├── If r < 0: decrease weight
        │   ├── Learning rate: 0.1
        │   └── Clamp to [0.1, 5.0]
        │
        └── brain._save() → brain.json updated
        │
        ▼
All future scoring uses updated weights:
  - TribeLeader weighs directives by learning_weights
  - Optimizer prioritizes high-weight regions
  - Creative agent focuses on high-weight triggers
  - Deploy readiness uses weight-adjusted scores
```

### Pipeline 6: Autonomous Loop (When Activated)

```
AutonomousLoop.run()
        │
        ▼
    ┌─── CHECK GOAL (GoalTracker)
    │    All criteria met? → GOAL_COMPLETE → stop
    │
    ├─── GET TASK (Strategist)
    │    ├── Check pending content → scoring tasks
    │    ├── Check low scores → optimization tasks
    │    ├── Check stale competitors → scout tasks
    │    ├── Check scores since last learn → learning tasks
    │    └── Check calibration schedule → calibration tasks
    │
    ├─── ROUTE MODEL (ModelRouter)
    │    ├── score task → sonnet
    │    ├── scout task → haiku
    │    ├── optimize task → sonnet
    │    ├── learn task → haiku
    │    └── creative task → opus
    │
    ├─── EXECUTE (via callback)
    │    └── Run the task through the appropriate agent
    │
    ├─── VALIDATE
    │    ├── Success → mark completed
    │    └── Failure → BlockResolver classifies error
    │        ├── resource → "try CPU fallback"
    │        ├── capability → "retry after 60s"
    │        ├── data → "skip and log"
    │        └── permission → "escalate to human"
    │
    └─── LOOP → back to CHECK GOAL

Campaign Coordinator manages state:
  DRAFT → SCORING → OPTIMIZING → RESCORING → REVIEW → APPROVED → DEPLOYED → COMPLETED
  Human review gate between RESCORING and APPROVED
```

---

## Data Flow: Source Separation

```
                    ┌─────────────────┐
                    │  Content Upload  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Is this yours? │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        source="own"    source="comp"    (future)
              │              │         source="universal"
              ▼              ▼
        ┌─────────┐   ┌──────────┐
        │ vault.db │   │ vault.db │
        │ own rows │   │ comp rows│
        └────┬────┘   └────┬─────┘
             │              │
             ▼              ▼
      ┌──────────────────────────────┐
      │    PatternExtractor          │
      │                              │
      │  Universal: ALL data         │ ← brain rules (both sources)
      │  Competitor: comp only       │ ← benchmarks
      │  Calibrated: own + metrics   │ ← YOUR truth
      └──────────────┬───────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌────▼────┐ ┌───▼──────┐
    │Universal│ │Compet.  │ │Calibrated│
    │Playbook │ │Benchmark│ │Niche     │
    │         │ │         │ │Playbook  │
    └─────────┘ └─────────┘ └────┬─────┘
                                  │
                                  ▼
                         AgentBrain.learning_weights
                         (ONLY updated from calibrated)
```

---

## Database Schema

### tribe.db (main scores)

```sql
scores:       id, filename, modality, overall_score, duration_seconds,
              visual_avg, auditory_avg, language_avg, decision_avg, emotion_avg,
              visual_pct, audio_pct, text_pct, hook_score, full_result (JSON), created_at

benchmarks:   id, category, metric, value, sample_size, updated_at
patterns:     id, pattern, confidence, evidence_count, discovered_at, last_confirmed
competitors:  id, name, url, last_scanned, content_count, avg_score, status
agent_logs:   id, agent, action, detail, created_at
```

### vault.db (pattern vault)

```sql
examples:     id, filename, modality, source ("own"/"competitor"),
              classification ("GOOD"/"BAD"/"NEUTRAL"), overall_score, hook_score,
              visual_avg, auditory_avg, language_avg, decision_avg, emotion_avg,
              visual_pct, audio_pct, text_pct, weak_moment_count, peak_moment_count,
              full_result (JSON), platform, audience_segment, tags, notes, created_at,
              real_ctr, real_conversion, real_watch_time
```

### knowledge_graph.db

```sql
episodes:     id, content, source, source_detail, valid_at, created_at, entities_json, relations_json
entities:     id, name, entity_type, summary, first_seen, last_seen, episode_count
edges:        id, source_entity, target_entity, relation, fact, valid_at, invalid_at, created_at
```

### content_map.db (lead classification)

```sql
content_profiles: url (PK), content_type, visual, auditory, language, decision, emotion,
                  face, action, social, attention, memory, conflict, reward,
                  dominant_region, dominant_score, visual_pct, audio_pct, text_pct,
                  tribe_score, hook_score, funnel_stage, scored_at
```

### JSON files (data/)

```
brain.json:     AgentBrain state (learning_weights, benchmarks, modality_insights, patterns)
goals.json:     GoalTracker state (objectives, criteria, progress)
patterns.json:  PatternVault discovered patterns (cached)
playbooks.json: Generated playbooks (cached)
```
