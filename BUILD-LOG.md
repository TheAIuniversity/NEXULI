# TRIBE Build Log — Errors, Fixes & Lessons

> Read this before building, debugging, or extending. Every error we hit is documented with root cause, fix, and what to watch for in the future.

---

## 2026-03-29 — Full Code Audit & Fix Round

### CRITICAL-1: TRIBE v2 package import fails
```
ModuleNotFoundError: No module named 'tribev2'
File: tribe_engine.py:36
```
**Root cause:** Meta's TRIBE v2 is a research repo, not a PyPI package. The import path `from tribev2.demo_utils import TribeModel` was guessed — the actual package name, class name, and method signatures were never verified against the real installed code.

**Fix applied:** Added two-level try/except with fallback to `tribe.demo_utils`. Added `TRIBE_AVAILABLE` flag. Clear error message with install instructions.

**Future risk:** When the Mac Mini arrives and TRIBE is actually installed, the real import path may differ. The class might not be called `TribeModel`. The method `from_pretrained()` might have different arguments. **First thing to do on Mac Mini: run `verify_tribe_install.py` test script before trusting anything.**

---

### CRITICAL-2: Timestamps doubled — 2Hz treated as 1Hz
```
scoring.py:110 — n_seconds = predictions.shape[0]
Every timestamp was 2x what it should be (30s video showed as 60s)
```
**Root cause:** TRIBE outputs at 2Hz (one prediction per 0.5 seconds). The code treated each row as 1 second. `atlas.py` correctly defined `TRIBE_TR_SECONDS = 0.5` but `scoring.py` never imported it.

**Fix applied:** Imported `TRIBE_TR_SECONDS` from `atlas.py`. All timestamps now use `float(i) * TRIBE_TR_SECONDS`. Hook analysis uses `int(3.0 / TRIBE_TR_SECONDS)` TRs for 3-second window.

**Future risk:** Any new code that reads TRIBE predictions must use `TRIBE_TR_SECONDS`, not assume 1 row = 1 second. grep for `predictions.shape[0]` to catch future occurrences.

---

### CRITICAL-3: REGION_MASKS were completely fictional
```
scoring.py:9-18 — REGION_MASKS = {"visual_cortex": (0, 2048), ...}
Vertex ranges were made up. Overlap between regions (prefrontal 8192-9216 and reward 8800-9216).
```
**Root cause:** fsaverage5 vertex ordering is based on mesh tessellation, not brain anatomy. Vertex 0 is NOT "visual cortex" — it's just the first vertex in the mesh file. The real mapping requires the HCP-MMP1 atlas which maps anatomical labels to specific vertex indices.

**Fix applied:** Replaced `REGION_MASKS` with `atlas.py` using `MARKETING_REGIONS` (12 clusters) mapped to real HCP region names. `get_vertex_atlas()` returns the actual vertex indices. Currently uses approximate mapping; will be replaced with exact MNE-derived mapping on Mac Mini.

**Future risk:** The current atlas mapping is still approximate (generated without MNE). When Mac Mini arrives, run `generate_brain_assets.py` with MNE installed to get exact vertex-to-region mapping. This will change all scores — expect numbers to shift.

---

### CRITICAL-4: PatternVault never received data
```
server.py:90-96 — scorer.score() saves to tribe.db but never calls vault.record_score()
The entire vault system (patterns, playbooks, calibration) stayed empty.
```
**Root cause:** The vault was built as a separate system but never wired into the main scoring flow in `server.py`. Two storage systems (`tribe.db` and `vault.db`) existed independently.

**Fix applied:** Added `vault.record_score()` call in `/api/score` endpoint after scoring. Added `source="own"` for own content, `source="competitor"` for competitor endpoint. Scorer agent also records to vault in its `score()` method.

**Future risk:** If new scoring paths are added (batch scoring, scheduled scoring, CLI scoring), they must ALL call `vault.record_score()`. grep for `scorer.score(` to find all paths.

---

### CRITICAL-5: TribeLeader was invisible — never exported
```
intelligence/__init__.py — tribe_leader.py not in imports
TribeAnalysis, generate_directives, score_deploy_readiness were dead code.
```
**Root cause:** File was created but never added to the package `__init__.py`.

**Fix applied:** Added export to `intelligence/__init__.py`.

**Future risk:** Every new module in any package must be added to its `__init__.py`. Check this for every new file.

---

### CRITICAL-6: Shallow copy corrupted DEFAULT_BRAIN
```
intelligence/brain.py:93 — self._data = DEFAULT_BRAIN.copy()
Shallow copy: nested dicts shared between instance and class default.
First update_from_score() mutated DEFAULT_BRAIN itself.
```
**Root cause:** Python's `dict.copy()` is shallow — nested dicts are shared references.

**Fix applied:** Changed to `copy.deepcopy(DEFAULT_BRAIN)`. Added `import copy`.

**Future risk:** Any module-level dict/list used as a default template MUST be deepcopied. grep for `.copy()` on nested structures.

---

### HIGH-1: Database connection leak in scorer
```
agents/scorer.py:44-53 — db.close() not called on exception path
```
**Root cause:** `db = get_db()` and `db.close()` were both inside the try block. If scoring failed, close was never reached.

**Fix applied:** Wrapped in `try/finally: db.close()`.

**Future risk:** All `get_db()` calls must use try/finally or context managers. Same pattern in `knowledge_graph.py` and `content_map.py` — those should be singletons to avoid the issue.

---

### HIGH-2: Fake calibration accuracy 0.73
```
agents/learner.py:72 — "calibration_accuracy": 0.73 if len(scores) > 10 else 0.0
Hardcoded number presented as real data.
```
**Root cause:** Placeholder that was never replaced with real computation.

**Fix applied:** Learner now delegates to `PatternVault.get_calibration_status()` which computes real readiness from actual paired data.

**Future risk:** Never ship hardcoded numbers that look like real metrics. If data isn't available yet, return `null` or `"not_ready"`, never a fake number.

---

### HIGH-4: Strategist generated zero tasks
```
orchestration/strategist.py:170-173 — pending_content and stale_competitors always empty lists
```
**Root cause:** Comments said "Populated by upload queue" but no code ever populated them. `assess_state()` always returned `[]`.

**Fix applied:** Now queries `scores` table for unoptimized recent scores and `competitors` table for stale entries (not scanned in 24h).

**Future risk:** When adding new task sources, always verify `assess_state()` actually queries for them.

---

### HIGH-5: Hard RESEARCHER cutoff at 8 pages
```
leads/classifier.py:281 — if len(interactions) >= 8: return BrainType.RESEARCHER
Decision Makers visiting 8+ pages got misclassified.
```
**Root cause:** Hard threshold before brain fingerprint analysis.

**Fix applied:** Changed to weighted signal: `researcher_score = 0.5*(page_count/12) + 0.5*(unique_urls/8)`, triggers at >= 0.6.

**Future risk:** Any classification heuristic should be a weighted signal, not a hard cutoff. Hard cutoffs create cliff edges that produce surprising misclassifications.

---

### HIGH-7: Two databases never synchronized
```
tribe.db (main scores) and vault.db (pattern vault) existed independently.
LearnerAgent read from tribe.db. PatternVault read from vault.db. Neither knew about the other.
```
**Root cause:** Vault was built as an isolated system. Scorer only wrote to tribe.db.

**Fix applied:** Scorer now writes to BOTH stores. vault.record_score() is called alongside save_score().

**Future risk:** If vault.db and tribe.db drift out of sync, pattern analysis will be based on incomplete data. Consider consolidating into one database long-term.

---

### HIGH-8: Rolling average used wrong count for modality buckets
```
intelligence/brain.py:129 — modality rolling average used total count, not per-bucket count
Visual-dominant average calculated with n=100 when only 10 items were visual-dominant.
```
**Root cause:** Single `n` counter used for all modality buckets.

**Fix applied:** Added `modality_counts` dict to DEFAULT_BRAIN with per-modality counters.

**Future risk:** The brain.json file must be reset (delete and let it regenerate) when the schema changes. Old brain.json files missing new fields will cause KeyError.

---

### HIGH-11: LearnerAgent ran primitive analysis, ignored PatternVault
```
agents/learner.py:38-48 — only checked one pattern (hook score), ignored PatternExtractor
```
**Root cause:** Original learner was a simple placeholder. Full PatternExtractor was built later but never wired in.

**Fix applied:** `analyze_scores()` now delegates to `PatternVault.run_analysis()`.

**Future risk:** When adding new analysis capabilities, add them to `PatternExtractor`, not to individual agents. The vault is the single source of truth for patterns.

---

### MEDIUM-2: Upload filename collisions
```
server.py:85 — file_path = settings.upload_dir / file.filename
Concurrent uploads with same name overwrite each other.
```
**Fix applied:** UUID prefix: `f"{uuid.uuid4().hex}_{file.filename}"`.

---

### RUNTIME: brain.json schema migration
```
KeyError: 'modality_counts'
Existing brain.json didn't have new fields added in the fix.
```
**Root cause:** Brain loads from existing JSON file, which was written before the schema change.

**Fix applied:** Deleted brain.json and let it regenerate from DEFAULT_BRAIN.

**Future risk:** ANY change to DEFAULT_BRAIN requires either: (a) delete existing brain.json, or (b) add migration code in `_load()` that patches missing keys.

---

### RUNTIME: python-multipart not installed
```
RuntimeError: Form data requires "python-multipart" to be installed.
Triggered when importing server.py with FastAPI file upload endpoints.
```
**Root cause:** `python-multipart` is in requirements.txt but not installed in the local dev environment.

**Fix:** `pip install python-multipart` before running the server. Already in requirements.txt for Mac Mini install.

---

### RUNTIME: goals.json schema incompatibility
```
TypeError: __init__() got an unexpected keyword argument
goals.py:62 — Goal(**gdata) crashes if JSON has extra fields from future schema.
```
**Root cause:** No field filtering when loading from JSON.

**Status:** Not yet fixed (MEDIUM-8). Recommended fix: `Goal(**{k: v for k, v in gdata.items() if k in Goal.__dataclass_fields__})`.

---

## Architecture Lessons Learned

1. **Build AND wire.** Building a module is 50% of the work. Wiring it into server.py + connecting to the data flow is the other 50%. 15 modules were built but never wired.

2. **One database, not two.** Having `tribe.db` and `vault.db` separate creates sync issues. Future: consolidate or add explicit sync.

3. **Never ship fake numbers.** A hardcoded `0.73` calibration accuracy looks real. If you don't have the data, say "not ready" — never invent metrics.

4. **Test the integration, not just the unit.** Every module passed import checks individually. The pipeline failed because they weren't connected.

5. **Atlas mapping is everything.** The REGION_MASKS being fictional meant every score was wrong. The atlas is the foundation — get it right first.

6. **Shallow copy kills.** `dict.copy()` on nested structures shares inner objects. Always `deepcopy()` for template defaults.

7. **Timestamp units must be explicit.** "Is this seconds or TRs? 1Hz or 2Hz?" — define the constant ONCE and import everywhere.
