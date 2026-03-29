# TRIBE Marketing Intelligence — How It's Built

## What This Is

A marketing intelligence system powered by Meta's TRIBE v2 brain encoding model. It predicts how human brains respond to content (video, audio, text) and converts those predictions into actionable marketing scores — attention curves, weak moments, hook analysis, modality breakdowns.

Built to replace $50,000-200,000 neuromarketing lab studies with a $0.50 GPU computation.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    FRONTEND                       │
│         JARVIS-style Dashboard (Next.js)          │
│  7 tabs: Command | Scanner | Creative | Scout     │
│          Agents | Learning | Chat                  │
└──────────────────┬───────────────────────────────┘
                   │ HTTP (localhost:8100)
┌──────────────────▼───────────────────────────────┐
│                 BACKEND (FastAPI)                  │
│  server.py → 13 API endpoints                     │
│  tribe_engine.py → TRIBE v2 model wrapper         │
│  scoring.py → brain predictions → marketing scores│
│  storage/db.py → SQLite persistence               │
├───────────────────────────────────────────────────┤
│                   6 AGENTS                         │
│  Scout → Competitor monitoring                     │
│  Creative → Brief generation from patterns         │
│  Scorer → TRIBE v2 content scoring                 │
│  Optimizer → Fix recommendations                   │
│  Deployer → Campaign deployment (stub)             │
│  Learner → Pattern discovery + calibration         │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│              TRIBE v2 ENGINE                       │
│  4 frozen encoders (loaded sequentially):          │
│  • LLaMA 3.2-3B (text, 3B params)                 │
│  • V-JEPA2 ViT-G (video, 1B params)               │
│  • Wav2Vec-BERT 2.0 (audio, 580M params)           │
│  • DINOv2-large (image, 300M params)               │
│  → Fusion Transformer (8 layers, 709 MB)           │
│  → 20,484 brain vertex predictions per second      │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│             OBSIDIAN KNOWLEDGE VAULT               │
│  27 files across 7 folders                         │
│  • Research (architecture, training, papers)        │
│  • Brain mapping (6 regions with marketing rules)  │
│  • Marketing (scoring framework, hook science)      │
│  • Agent documentation (6 agents)                  │
│  • Patterns (21 discovered patterns)               │
│  • Templates (score + competitor templates)         │
└──────────────────────────────────────────────────┘
```

---

## File Structure

```
/Users/sven/Desktop/TRIBE/
├── dashboard.tsx                    # Frontend (JARVIS dark theme, 1,550 lines)
├── HOW-ITS-BUILT.md                # This file
├── ONGOING-PROGRESS.md             # What's done, what's next
│
├── backend/
│   ├── server.py                   # FastAPI server, 13 endpoints, port 8100
│   ├── tribe_engine.py             # Singleton TRIBE model wrapper, lazy-loads
│   ├── scoring.py                  # Brain → marketing score conversion (core IP)
│   ├── config.py                   # Pydantic settings, env vars with TRIBE_ prefix
│   ├── requirements.txt            # Python dependencies
│   ├── agents/
│   │   ├── __init__.py             # Agent registry
│   │   ├── scorer.py               # TRIBE scoring agent
│   │   ├── optimizer.py            # Recommendation generator
│   │   ├── learner.py              # Pattern discovery + calibration
│   │   ├── scout.py                # Competitor tracker
│   │   ├── creative.py             # Brief generator
│   │   └── deployer.py             # Campaign deployment (stub)
│   └── storage/
│       ├── __init__.py             # Storage exports
│       └── db.py                   # SQLite (5 tables: scores, benchmarks, patterns, competitors, agent_logs)
│
└── vault/                          # Obsidian knowledge vault (27 files)
    ├── README.md                   # Vault index
    ├── research/                   # TRIBE v2 papers + architecture
    │   ├── TRIBE-v2-Architecture.md
    │   ├── TRIBE-v2-Training.md
    │   ├── TRIBE-v2-Brain-Regions.md
    │   ├── TRIBE-v2-Inference-Pipeline.md
    │   └── Meta-FAIR-Papers.md
    ├── brain-mapping/              # Brain region → marketing mapping
    │   ├── Visual-Cortex.md
    │   ├── Auditory-Cortex.md
    │   ├── Language-Areas.md
    │   ├── Prefrontal-Cortex.md
    │   ├── Default-Mode-Network.md
    │   └── Fusiform-Face-Area.md
    ├── marketing/                  # Scoring frameworks + content science
    │   ├── Content-Scoring-Framework.md
    │   ├── Modality-Analysis.md
    │   ├── Hook-Science.md
    │   ├── Attention-Curves.md
    │   └── Weak-Moment-Patterns.md
    ├── agents/                     # Agent documentation
    │   ├── Scout-Agent.md
    │   ├── Creative-Agent.md
    │   ├── TRIBE-Scorer-Agent.md
    │   ├── Optimizer-Agent.md
    │   ├── Deployer-Agent.md
    │   └── Learner-Agent.md
    ├── patterns/                   # Discovered patterns + calibration
    │   ├── Discovered-Patterns.md
    │   └── Calibration-Log.md
    └── templates/                  # Obsidian templates
        ├── Content-Score-Template.md
        └── Competitor-Analysis-Template.md
```

---

## How The Scoring Pipeline Works

### Input
Any video (.mp4, .avi, .mov), audio (.wav, .mp3), or text (.txt) file.

### Step 1: TRIBE Feature Extraction
File → 4 frozen encoders run sequentially:
- Video through V-JEPA2 (1B params) → 1,280-dim features at 2 Hz
- Audio through Wav2Vec-BERT 2.0 → 1,024-dim features at 2 Hz
- Text transcribed via WhisperX → words through LLaMA 3.2-3B → 2,048-dim features at 2 Hz
- Key frames through DINOv2 → image features

Each encoder loads, extracts, caches to disk, then frees GPU memory before next encoder.

### Step 2: Fusion Transformer
Concatenated features → 8-layer transformer (1,152 hidden dim) → predictions for 20,484 brain surface vertices per second of content.

### Step 3: Brain → Marketing Conversion (scoring.py)
Raw 20,484 vertex predictions split into brain regions:
- Visual cortex (vertices 0-2,048) → visual engagement score
- Auditory cortex (vertices 4,096-5,120) → audio engagement score
- Broca's + Wernicke's → language processing score
- Prefrontal cortex → decision-making score
- Default mode network → emotional resonance score
- Fusiform face area → face detection response

Weighted combination → overall attention score per second (0-100).

### Step 4: Moment Detection
- Weak moments: attention < 40 for 2+ consecutive seconds → tagged with cause + fix
- Peak moments: attention > 80 for 2+ consecutive seconds → tagged as hook/thumbnail/clip
- Hook score: average attention in first 3 seconds
- Modality mix: which brain systems are carrying the response (visual vs audio vs text %)

### Output
```json
{
  "overall_score": 78,
  "duration_seconds": 30,
  "per_second": [{"timestamp": 0, "attention": 82, "visual": 65, ...}, ...],
  "visual_pct": 35, "audio_pct": 45, "text_pct": 20,
  "weak_moments": [{"start": 12, "end": 15, "reason": "...", "recommendation": "..."}],
  "peak_moments": [{"start": 4, "end": 7, "reason": "...", "use_case": "hook"}],
  "hook_score": 85,
  "recommendations": [{"priority": "high", "fix": "..."}]
}
```

---

## API Endpoints (server.py, port 8100)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/score` | Upload + score content through TRIBE |
| GET | `/api/scores` | Score history |
| GET | `/api/health` | System + model status |
| GET | `/api/agents` | All agent statuses |
| GET | `/api/agents/{name}/logs` | Agent activity logs |
| GET | `/api/patterns` | Discovered patterns |
| POST | `/api/learn` | Trigger pattern analysis |
| GET | `/api/competitors` | Tracked competitors |
| POST | `/api/competitors` | Add competitor |
| GET | `/api/feed` | Activity feed |
| POST | `/api/brief` | Generate creative brief |
| POST | `/api/tribe/load` | Explicitly preload TRIBE model |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + TypeScript + Framer Motion (JARVIS dark theme) |
| Backend API | FastAPI (Python) |
| AI Model | TRIBE v2 (Meta FAIR) — 709 MB fusion model + 4 frozen encoders |
| Database | SQLite with WAL mode |
| Knowledge Base | Obsidian vault (27 markdown files with wikilinks) |
| Feature Extractors | LLaMA 3.2-3B, V-JEPA2, Wav2Vec-BERT 2.0, DINOv2-large |
| Transcription | WhisperX (word-level timestamps) |

---

## Hardware Requirements

| Task | Minimum |
|------|---------|
| TRIBE inference | 6+ GB VRAM (Mac Mini M4 with 16 GB works) |
| Peak VRAM (V-JEPA2 extraction) | ~4-6 GB |
| Fusion model inference | ~2-3 GB |
| Disk (model cache) | ~15 GB for all backbone downloads |
| Scoring speed | ~5-10 min per minute of video content on M-series Mac |

---

## How To Start

```bash
# 1. Install dependencies
cd /Users/sven/Desktop/TRIBE/backend
pip install -r requirements.txt

# 2. Start the API server
python server.py
# → http://localhost:8100/docs (Swagger UI with all endpoints)

# 3. Open the Obsidian vault
# Open Obsidian → Open folder as vault → /Users/sven/Desktop/TRIBE/vault/

# 4. Score your first content
curl -X POST http://localhost:8100/api/score -F "file=@my_ad.mp4"

# 5. Open the dashboard
# dashboard.tsx runs inside the Next.js app at /marketing
```
