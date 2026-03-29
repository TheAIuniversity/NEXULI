# Nexuli — Marketing Intelligence Powered by Neuroscience

**Predict how human brains respond to your content before you spend a dollar.**

Nexuli uses Meta's TRIBE v2 brain encoding model — trained on 720 human brains and 1,115 hours of fMRI data — to score your videos, audio, and text across 20,484 cortical brain locations. Know exactly which second loses attention, which modality carries engagement, and what triggers the decision to buy.

Replace $50,000 neuromarketing lab studies with a 5-minute computation on a Mac Mini.

---

## What It Does

Upload any content → Nexuli predicts brain activation across 12 cognitive systems → You get actionable scores, weak moments, fix recommendations, and competitive intelligence.

```
Your ad (video/audio/text)
        ↓
    TRIBE v2 Engine
    (LLaMA 3.2 + V-JEPA2 + Wav2Vec-BERT + DINOv2)
        ↓
    20,484 brain vertex predictions at 2Hz
        ↓
    12 Marketing Brain Regions
    ┌────────────────────────────────────┐
    │ Visual Processing      78%        │
    │ Auditory Processing    65%        │
    │ Language Comprehension  82%        │
    │ Decision Making        71%  ← CTA │
    │ Emotional Resonance    58%        │
    │ Face Recognition       89%  ← Hook│
    │ Action Impulse         45%        │
    │ Social Cognition       62%        │
    │ Attention & Salience   74%        │
    │ Memory Encoding        51%        │
    │ Conflict & Motivation  67%        │
    │ Reward Processing      73%        │
    └────────────────────────────────────┘
        ↓
    "Attention drops at 0:12 — visual cortex flat,
     no scene change for 6 seconds. Add a face or
     visual cut. Move CTA to 0:22 where prefrontal
     peaks. Audio carrying 52% — visuals underperforming."
```

## Key Features

### Brain-Level Content Scoring
Score any video, audio, or text through TRIBE. Get per-second brain activation curves across 360 HCP-MMP1 brain regions grouped into 12 marketing-relevant clusters. Know exactly where attention drops, which modality carries engagement, and when the decision impulse fires.

### True Modality Ablation
Don't guess which channel matters — measure it. TRIBE runs your content with each modality (visual/audio/text) zeroed out to compute the true contribution of each. "Audio carries 52% of brain response. Visuals only 31%. Your video is actually a podcast with pictures."

### Temporal Dynamics
The 8-layer fusion transformer captures cross-second patterns. Does a visual hook at second 3 drive decision-making at second 8? Is engagement momentum building or decaying? How smooth is the attention flow?

### Pattern Vault with Source Separation
Every scored piece feeds a self-improving pattern database with strict data separation:
- **Universal patterns** — brain rules from all content (own + competitor)
- **Competitor benchmarks** — market intelligence, never mixed with your calibration
- **Calibrated patterns** — YOUR content + YOUR real metrics = YOUR truth

The system gets smarter with every piece of content scored.

### TRIBE-Led Agent Directives
TRIBE brain maps don't just produce scores — they DRIVE every agent decision. The optimizer doesn't say "improve this section." It says "prefrontal cortex dropped at 0:12 because there's nothing to evaluate — add a question or statistic." Every recommendation traces back to a specific brain region and its learned weight.

### Lead Classification by Brain Type
Score your website pages through TRIBE. When leads visit, their content consumption pattern reveals their brain type:
- 🧠 **Decision Maker** — consumes pricing, comparisons, CTAs → ready to buy
- ❤️ **Emotional Connector** — consumes testimonials, stories → needs trust
- 👁️ **Visual Scanner** — watches demos, scrolls fast → show, don't tell
- 🎧 **Audio Processor** — listens to podcasts, webinars → wants conversation
- 🔬 **Researcher** — reads everything → needs comprehensive information

Each type gets hyper-targeted follow-up actions with brain-evidence reasoning.

### 3D Brain Visualization
Real fsaverage5 pial cortical mesh (20,484 vertices, 40,960 triangles) rendered in the browser with React Three Fiber. Gray brain base, activated regions light up in fMRI-style colors. Click any region → see what emotion it triggers, why it activated, and how to optimize for it. Side-by-side comparison with per-scan navigation.

### Audience Archetypes
TRIBE was trained on 25 subjects across 4 studies. Each subject learned a different brain-to-content mapping:
- **Visual Engagers** (Algonauts subjects) — movie watchers, face-responsive
- **Audio Learners** (Lebel subjects) — podcast listeners, language-dominant
- **Sustained Viewers** (Wen subjects) — long-form video processors
- **Quick Scanners** (Lahner subjects) — short-clip rapid assessors

Score content per archetype to know which audience type responds best.

### Self-Improving Calibration
Pair TRIBE brain scores with real-world performance (CTR, conversion, watch time). The system discovers which brain regions actually predict YOUR business outcomes and adjusts its weights accordingly. After 100 calibrated samples, it predicts YOUR conversion rate from brain activation.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    FRONTEND                           │
│         20-tab Intel-style Dashboard                  │
│  Command | Scanner | Creative | Scout | Agents        │
│  Learning | Chat | Ad Gen | Launcher | Funnels        │
│  Audiences | Viral | A/B Lab | Email | War Room       │
│  Calendar | Landing | Simulate | Brain | Vault | Leads│
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│              FASTAPI BACKEND (22 endpoints)            │
│  Score → Analyze → Learn → Recommend → Deploy          │
├───────────────────────────────────────────────────────┤
│  6 Agents: Scorer, Optimizer, Learner, Scout,          │
│           Creative, Deployer                           │
├───────────────────────────────────────────────────────┤
│  Intelligence: Brain, KnowledgeGraph, Scraper,         │
│               Compression, Engagement, Dedup,          │
│               TribeLeader                              │
├───────────────────────────────────────────────────────┤
│  Orchestration: AutonomousLoop, Strategist,            │
│                Coordinator, Goals, BlockResolver        │
├───────────────────────────────────────────────────────┤
│  Pattern Vault: ExampleStore, PatternExtractor,        │
│                PlaybookGenerator (3-scope separation)   │
├───────────────────────────────────────────────────────┤
│  Leads: ContentBrainMap, LeadClassifier,               │
│         HyperTargeter (5 brain types)                  │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│              TRIBE v2 ENGINE                           │
│  LLaMA 3.2-3B | V-JEPA2 ViT-G | Wav2Vec-BERT 2.0    │
│  DINOv2-large | 8-layer Fusion Transformer             │
│  → 20,484 brain vertex predictions per second          │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│           OBSIDIAN KNOWLEDGE VAULT                     │
│  28 files: research, brain mapping, marketing          │
│  frameworks, agent docs, patterns, templates           │
└──────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Meta TRIBE v2 (709 MB fusion model + 4 frozen encoders) |
| Feature Extractors | LLaMA 3.2-3B, V-JEPA2 ViT-G, Wav2Vec-BERT 2.0, DINOv2-large |
| Brain Atlas | HCP-MMP1 (360 regions) on fsaverage5 mesh (20,484 vertices) |
| Backend | Python, FastAPI, SQLite (WAL mode) |
| Frontend | React, TypeScript, Framer Motion, React Three Fiber |
| 3D Visualization | Three.js with real fsaverage5 pial cortical mesh |
| Knowledge Base | Obsidian-compatible markdown vault with wikilinks |
| Transcription | WhisperX (word-level timestamps) |

## Hardware Requirements

| | Minimum | Recommended |
|---|---|---|
| **Machine** | Mac Mini M4 16GB | Mac Mini M4 Pro 24GB |
| **VRAM** | 6 GB (MPS) | 16 GB+ |
| **Disk** | 20 GB (model cache) | 50 GB |
| **Inference speed** | ~5-10 min per minute of video | Faster with more RAM |

## Quick Start

```bash
# Clone
git clone https://github.com/TheAIuniversity/NEXULI.git
cd TRIBE

# Install backend
cd backend
pip install -r requirements.txt

# Start API server
python server.py
# → http://localhost:8100/docs

# Score your first content
curl -X POST http://localhost:8100/api/score -F "file=@your_ad.mp4"
```

> **Note:** TRIBE v2 model weights (~15 GB) download automatically on first use. Requires HuggingFace account with LLaMA 3.2 access approved.

## API

22 endpoints. Full documentation in [API-ENDPOINTS.md](API-ENDPOINTS.md).

```bash
# Score own content
POST /api/score                    → Upload + brain score

# Score competitor content (separated data)
POST /api/score/competitor         → Score + tag as competitor

# Pattern learning
POST /api/vault/analyze            → Extract patterns from all scored content
GET  /api/vault/patterns           → Discovered patterns by scope
GET  /api/vault/calibration        → Calibration readiness

# Lead classification
POST /api/leads/classify           → Brain-type classification + actions

# System
GET  /api/health                   → TRIBE model status + agent health
```

## Data Separation

Nexuli enforces strict separation between data sources to prevent false signals:

| Source | What It Contains | Used For |
|--------|-----------------|----------|
| **Universal** | Brain scores from ALL content | Brain-level creative rules |
| **Competitor** | Competitor content scores (no real metrics) | Benchmarking only |
| **Calibrated** | YOUR content + YOUR real performance data | YOUR truth — learning weights, niche patterns, deploy decisions |

The calibration pipeline **never** mixes competitor scores with your conversion data. Learning weights are **only** updated from calibrated (own) data.

## The Science

TRIBE v2 was developed by Meta FAIR and published in March 2026. It won 1st place at Algonauts 2025 (263 teams). The model:

- Predicts brain activity from video, audio, and text stimuli
- Trained on 451.6 hours of fMRI from 25 subjects, evaluated on 720
- Captures 54% of explainable brain variance
- Uses frozen state-of-the-art encoders (LLaMA 3.2, V-JEPA2, Wav2Vec-BERT)
- Recovers known neuroscience findings without being explicitly trained on them

The marketing application is novel: nobody has previously used a brain encoding model to predict content performance at scale. The calibration pipeline (correlating brain scores with real CTR/conversion) is the validation step that determines commercial viability.

Read more: [Meta Research Paper](https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/) | [Meta Blog](https://ai.meta.com/blog/tribe-v2-brain-predictive-foundation-model/) | [GitHub](https://github.com/facebookresearch/tribev2)

## Project Structure

```
NEXULI/
├── backend/
│   ├── server.py              # FastAPI server (22 endpoints)
│   ├── tribe_engine.py        # TRIBE v2 model wrapper
│   ├── scoring.py             # Brain → marketing scores (HCP atlas)
│   ├── atlas.py               # 360 HCP-MMP1 regions → 12 marketing clusters
│   ├── agents/                # 6 autonomous agents
│   ├── intelligence/          # Brain, KG, scraper, compression, TribeLeader
│   ├── orchestration/         # Loop, strategist, coordinator, goals
│   ├── vault/                 # Pattern vault with source separation
│   ├── leads/                 # Brain-type lead classifier
│   ├── ablation.py            # True modality contribution measurement
│   ├── embeddings.py          # 1152-dim + 2048-dim content fingerprints
│   ├── audience.py            # 25 subjects → 4 audience archetypes
│   ├── temporal.py            # Cross-second dynamics analysis
│   ├── rgb_brain.py           # R=text G=audio B=video brain overlay
│   └── segment_mapper.py      # Word-level brain impact attribution
├── vault/                     # Obsidian knowledge vault (28 files)
│   ├── research/              # TRIBE architecture, training, papers
│   ├── brain-mapping/         # 6 brain regions with marketing rules
│   ├── marketing/             # Scoring framework, hook science, patterns
│   ├── agents/                # Agent documentation
│   └── patterns/              # Discovered patterns + calibration log
├── dashboard.tsx              # 20-tab Intel-style control room
├── dashboard-workflows.tsx    # Tab components (3,500+ lines)
├── HOW-ITS-BUILT.md          # Architecture documentation
├── API-ENDPOINTS.md           # Full API reference + pipeline diagrams
├── BUILD-LOG.md               # Every error encountered + fix + lesson
└── ONGOING-PROGRESS.md        # What's done, what's next
```

## Status

The Nexuli platform architecture is complete. Waiting for hardware (Mac Mini M4) to activate the TRIBE v2 model for live inference.

**Built:** Backend (48 Python files), Frontend (20 tabs), Vault (28 files), 3D Brain Viewer
**Audited:** Full code audit completed — 6 critical + 11 high issues found and fixed
**Next:** Install TRIBE v2 on Mac Mini → calibrate atlas → score first content → begin calibration study

See [ONGOING-PROGRESS.md](ONGOING-PROGRESS.md) for the full 9-phase roadmap.

## License

The Nexuli codebase (this repository) is open source.

Meta's TRIBE v2 pre-trained model weights are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (non-commercial). The frozen encoders (V-JEPA2, Wav2Vec-BERT, DINOv2) are commercially licensed. For commercial use, train your own fusion weights on your own data (see Phase 8 in ONGOING-PROGRESS.md).

## Built With

Built by [The AI University](https://theaiuniversity.com) using [Claude Code](https://claude.ai/claude-code).
