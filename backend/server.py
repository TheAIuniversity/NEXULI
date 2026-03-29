"""TRIBE Marketing Intelligence API."""

import uuid
import shutil
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from tribe_engine import TribeEngine
from storage import get_db, get_scores, get_patterns, get_agent_logs
from agents import ALL_AGENTS
from vault import PatternVault

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# Instantiate all agents once at import time
agents = {name: cls() for name, cls in ALL_AGENTS.items()}
vault = PatternVault()

ALLOWED_EXTENSIONS = {
    ".mp4", ".avi", ".mkv", ".mov", ".webm",   # video
    ".wav", ".mp3", ".flac", ".ogg",            # audio
    ".txt",                                      # text
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TRIBE Marketing Intelligence starting...")
    logger.info(f"Upload dir : {settings.upload_dir}")
    logger.info(f"Database   : {settings.db_path}")
    logger.info("TRIBE model will load lazily on first /api/score request.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="TRIBE Marketing Intelligence",
    version="1.0.0",
    description="Brain-encoding content scoring via Meta's TRIBE v2 model.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["system"])
async def health():
    """Service health + agent overview."""
    engine = TribeEngine.get()
    return {
        "status": "online",
        "tribe_loaded": engine.is_loaded,
        "agents": {name: a.get_status() for name, a in agents.items()},
    }


# ── Score Content ─────────────────────────────────────────────────────────────

@app.post("/api/score", tags=["scoring"])
async def score_upload(file: UploadFile = File(...)):
    """Upload a media file and score it through TRIBE v2.

    Supported formats: mp4, avi, mkv, mov, webm, wav, mp3, flac, ogg, txt.

    Returns the full ContentScore plus optimizer recommendations.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    file_path = settings.upload_dir / f"{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        scorer = agents["scorer"]
        result = scorer.score(str(file_path))
        vault.record_score(result, filename=file.filename, modality=ext.lstrip('.'), source="own")

        optimizer = agents["optimizer"]
        recommendations = optimizer.optimize(result)

        return {"score": result, "recommendations": recommendations}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Scoring pipeline failed for {file.filename}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")
    finally:
        if file_path.exists():
            file_path.unlink()


# ── Scores History ────────────────────────────────────────────────────────────

@app.get("/api/scores", tags=["scoring"])
async def list_scores(limit: int = Query(default=50, ge=1, le=500)):
    """Retrieve recent scoring history."""
    db = get_db()
    scores = get_scores(db, limit=limit)
    db.close()
    return scores


# ── Model Loading ─────────────────────────────────────────────────────────────

@app.post("/api/tribe/load", tags=["system"])
async def load_tribe():
    """Explicitly warm up the TRIBE model (takes 30-60 s on first call).

    Subsequent calls are no-ops and return immediately.
    """
    engine = TribeEngine.get()
    if engine.is_loaded:
        return {"status": "already_loaded"}
    engine.load()
    return {"status": "loaded"}


# ── Agents ────────────────────────────────────────────────────────────────────

@app.get("/api/agents", tags=["agents"])
async def list_agents():
    """Return status for all agents."""
    return {name: a.get_status() for name, a in agents.items()}


@app.get("/api/agents/{agent_name}/logs", tags=["agents"])
async def agent_logs(agent_name: str, limit: int = Query(default=50, ge=1, le=1000)):
    """Return activity logs for a specific agent."""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name}")
    db = get_db()
    logs = get_agent_logs(db, agent=agent_name, limit=limit)
    db.close()
    return logs


# ── Patterns / Learning ───────────────────────────────────────────────────────

@app.get("/api/patterns", tags=["learning"])
async def list_patterns():
    """Return learned patterns sorted by confidence."""
    db = get_db()
    patterns = get_patterns(db)
    db.close()
    return patterns


@app.post("/api/learn", tags=["learning"])
async def trigger_learning():
    """Run the learner agent over all stored scores to surface new patterns."""
    result = vault.run_analysis()
    calibration = vault.get_calibration_status()
    return {"analysis": result, "calibration": calibration}


# ── Vault ─────────────────────────────────────────────────────────────────────

@app.get("/api/vault/stats", tags=["vault"])
async def vault_stats():
    return vault.get_stats()


@app.get("/api/vault/patterns", tags=["vault"])
async def vault_patterns(scope: str = None, status: str = None, category: str = None):
    return vault.get_patterns(scope=scope, status=status, category=category)


@app.get("/api/vault/playbooks", tags=["vault"])
async def vault_playbooks():
    return vault.get_playbooks()


@app.get("/api/vault/examples", tags=["vault"])
async def vault_examples(source: str = None, classification: str = None, limit: int = 100):
    return vault.get_examples(source=source, classification=classification, limit=limit)


@app.post("/api/vault/analyze", tags=["vault"])
async def vault_analyze():
    result = vault.run_analysis()
    return result


@app.get("/api/vault/guidelines", tags=["vault"])
async def vault_guidelines(scope: str = None):
    return vault.get_creative_guidelines(scope=scope)


@app.get("/api/vault/calibration", tags=["vault"])
async def vault_calibration():
    return vault.get_calibration_status()


# ── Leads ─────────────────────────────────────────────────────────────────────

@app.post("/api/leads/classify", tags=["leads"])
async def classify_lead(lead_id: str, interactions: list):
    from leads import LeadClassifier, ContentInteraction, ContentBrainMap, HyperTargeter
    cm = ContentBrainMap()
    classifier = LeadClassifier(cm)
    parsed = [ContentInteraction(**i) for i in interactions]
    profile = classifier.classify(lead_id, parsed)
    targeter = HyperTargeter()
    actions = targeter.generate_actions(profile)
    return {"profile": profile.to_dict(), "actions": [a.to_dict() for a in actions]}


@app.get("/api/leads/content-map", tags=["leads"])
async def content_map_stats():
    from leads import ContentBrainMap
    cm = ContentBrainMap()
    return cm.get_stats()


# ── Score competitor content ───────────────────────────────────────────────────

@app.post("/api/score/competitor", tags=["scoring"])
async def score_competitor(file: UploadFile = File(...), competitor_name: str = ""):
    """Score competitor content — saved with source='competitor'."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    file_path = settings.upload_dir / f"{uuid.uuid4().hex}_{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        scorer = agents["scorer"]
        result = scorer.score(str(file_path))
        vault.record_score(result, filename=file.filename, modality=ext.lstrip('.'), source="competitor")
        return {"score": result, "source": "competitor"}
    except Exception as e:
        raise HTTPException(500, f"Scoring failed: {str(e)}")
    finally:
        if file_path.exists():
            file_path.unlink()


# ── Competitors ───────────────────────────────────────────────────────────────

@app.get("/api/competitors", tags=["scout"])
async def list_competitors():
    """List all active competitors being tracked."""
    scout = agents["scout"]
    return scout.get_competitors()


@app.post("/api/competitors", tags=["scout"])
async def add_competitor(name: str, url: str = None):
    """Add a new competitor to the watchlist."""
    scout = agents["scout"]
    scout.add_competitor(name, url)
    return {"status": "added", "name": name}


# ── Creative Briefs ───────────────────────────────────────────────────────────

@app.post("/api/brief", tags=["creative"])
async def generate_brief(
    content_type: str = Query(default="video"),
    target_score: int = Query(default=80, ge=0, le=100),
):
    """Generate a creative brief informed by learned patterns."""
    creative = agents["creative"]
    brief = creative.generate_brief(content_type, target_score)
    return brief


# ── Activity Feed ─────────────────────────────────────────────────────────────

@app.get("/api/feed", tags=["system"])
async def activity_feed(limit: int = Query(default=50, ge=1, le=1000)):
    """Global agent activity feed, newest first."""
    db = get_db()
    logs = get_agent_logs(db, limit=limit)
    db.close()
    return logs


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )
