# TRIBE v2 Marketing Intelligence Backend

Production-ready FastAPI backend that wraps Meta's TRIBE v2 brain encoding model
and converts its neural predictions into actionable marketing scores.

## Stack

- **FastAPI 0.115** — async REST API
- **TRIBE v2** — Meta's brain encoding model (scores content against 20,484 cortical vertices)
- **SQLite (WAL mode)** — scores, patterns, benchmarks, agent logs
- **6 autonomous agents** — scorer, optimizer, learner, scout, creative, deployer

## Quick Start

```bash
cd /Users/sven/Desktop/TRIBE/backend

# Install dependencies
pip install -r requirements.txt

# Start server (port 8100)
python server.py
# or
uvicorn server:app --host 0.0.0.0 --port 8100
```

Open `http://localhost:8100/docs` for the interactive Swagger UI.

## Environment Variables

All variables are prefixed with `TRIBE_`:

| Variable           | Default         | Description                              |
|--------------------|-----------------|------------------------------------------|
| `TRIBE_CACHE`      | `./cache`       | Where TRIBE model weights are cached     |
| `TRIBE_DEVICE`     | `auto`          | `auto`, `cpu`, `cuda`, or `mps`          |
| `TRIBE_UPLOAD_DIR` | `./uploads`     | Temporary storage for uploaded files     |
| `TRIBE_DB_PATH`    | `./data/tribe.db` | SQLite database path                   |
| `TRIBE_HOST`       | `0.0.0.0`       | Bind address                             |
| `TRIBE_PORT`       | `8100`          | Port                                     |

## API Endpoints

### Scoring

| Method | Path          | Description                                          |
|--------|---------------|------------------------------------------------------|
| POST   | `/api/score`  | Upload a media file; returns score + recommendations |
| GET    | `/api/scores` | Scoring history (`?limit=50`)                        |

Supported file types: `mp4 avi mkv mov webm wav mp3 flac ogg txt`

Example response from `/api/score`:

```json
{
  "score": {
    "overall_score": 74,
    "duration_seconds": 30,
    "hook_score": 82.1,
    "hook_frame": 2,
    "visual_avg": 68.4,
    "auditory_avg": 71.2,
    "language_avg": 55.0,
    "decision_avg": 60.1,
    "emotion_avg": 58.7,
    "visual_pct": 38.1,
    "audio_pct": 39.6,
    "text_pct": 22.3,
    "weak_moments": [...],
    "peak_moments": [...],
    "per_second": [...]
  },
  "recommendations": [
    {
      "priority": "medium",
      "area": "12s-16s",
      "issue": "Overall attention below threshold for 4s.",
      "fix": "Shorten this section or add engagement triggers."
    }
  ]
}
```

### Agents

| Method | Path                          | Description             |
|--------|-------------------------------|-------------------------|
| GET    | `/api/agents`                 | Status of all agents    |
| GET    | `/api/agents/{name}/logs`     | Logs for a single agent |

### Learning

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| GET    | `/api/patterns`| Learned patterns sorted by confidence   |
| POST   | `/api/learn`   | Trigger learner analysis                 |

### Scout

| Method | Path               | Description               |
|--------|--------------------|---------------------------|
| GET    | `/api/competitors` | List tracked competitors  |
| POST   | `/api/competitors` | Add a competitor          |

### Creative

| Method | Path         | Description                                        |
|--------|--------------|----------------------------------------------------|
| POST   | `/api/brief` | Generate a creative brief from learned patterns    |

### System

| Method | Path              | Description                            |
|--------|-------------------|----------------------------------------|
| GET    | `/api/health`     | Health check + agent overview          |
| POST   | `/api/tribe/load` | Pre-warm the TRIBE model (~30-60 s)    |
| GET    | `/api/feed`       | Global agent activity log              |

## Brain Region Mapping

TRIBE outputs activations across ~20,484 cortical vertices (fsaverage5 surface).
`scoring.py` maps these to marketing-relevant regions:

| Region             | Vertices     | Marketing Signal           |
|--------------------|--------------|----------------------------|
| Visual cortex      | 0 – 2048     | Visual engagement          |
| Fusiform face area | 2048 – 2560  | Face/person response       |
| Auditory cortex    | 4096 – 5120  | Audio engagement           |
| Wernicke's area    | 5120 – 5632  | Language comprehension     |
| Broca's area       | 7168 – 7680  | Language production/recall |
| Prefrontal cortex  | 8192 – 9216  | Decision-making            |
| Default mode       | 9216 – 10240 | Self-reference / emotion   |

Overall attention is the weighted average:
`0.25 × visual + 0.20 × auditory + 0.20 × language + 0.20 × decision + 0.15 × emotion`

## Agents

| Agent      | Role                                                        |
|------------|-------------------------------------------------------------|
| `scorer`   | Runs TRIBE inference, persists results to DB                |
| `optimizer`| Reads scores, emits prioritised fix recommendations         |
| `learner`  | Cross-analyzes scores to surface statistical patterns       |
| `scout`    | Tracks competitor watchlist                                 |
| `creative` | Generates data-driven creative briefs                       |
| `deployer` | Stub for future ad-platform deployment integration          |

## Project Layout

```
backend/
├── server.py          FastAPI application + all route handlers
├── tribe_engine.py    Singleton TRIBE model wrapper (lazy-loads)
├── scoring.py         Vertex → marketing score conversion
├── config.py          Pydantic settings with TRIBE_ env prefix
├── requirements.txt
├── agents/
│   ├── scorer.py
│   ├── optimizer.py
│   ├── learner.py
│   ├── scout.py
│   ├── creative.py
│   └── deployer.py
└── storage/
    └── db.py          SQLite helpers (WAL, schema migrations)
```
