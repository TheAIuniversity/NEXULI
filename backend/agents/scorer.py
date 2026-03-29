"""TRIBE Scoring Agent — scores content through TRIBE v2."""

import logging
from pathlib import Path
from tribe_engine import TribeEngine
from scoring import score_content
from storage import get_db, save_score, log_agent
from vault import PatternVault

logger = logging.getLogger(__name__)


class ScorerAgent:
    name = "scorer"
    description = "Scores content through TRIBE v2 brain encoding model"

    def __init__(self):
        self.engine = TribeEngine.get()
        self.vault = PatternVault()
        self.status = "idle"
        self.scored_count = 0

    def score(self, file_path: str) -> dict:
        """Score a single content file.

        Args:
            file_path: Absolute path to the media file.

        Returns:
            ContentScore serialised as a dict.

        Raises:
            ValueError: For unsupported file types.
            RuntimeError: If the TRIBE model fails to produce predictions.
        """
        self.status = "scoring"
        logger.info(f"Scoring: {file_path}")

        try:
            result = self.engine.predict(file_path)
            predictions = result["predictions"]
            segments = result["segments"]

            content_score = score_content(predictions, segments)
            score_dict = content_score.to_dict()

            db = get_db()
            try:
                save_score(db, Path(file_path).name, result["modality"], score_dict)
                log_agent(
                    db,
                    self.name,
                    "content-scored",
                    f"{Path(file_path).name}: {score_dict['overall_score']}/100",
                )
            finally:
                db.close()

            # Record into PatternVault for pattern learning
            try:
                self.vault.record_score(
                    score_dict,
                    filename=Path(file_path).name,
                    modality=result["modality"],
                    source="own",
                )
            except Exception as vault_err:
                logger.warning(f"Vault recording failed (non-fatal): {vault_err}")

            self.scored_count += 1
            self.status = "idle"
            return score_dict

        except Exception as e:
            self.status = "error"
            logger.error(f"Scoring failed: {e}")
            raise

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "scored_count": self.scored_count,
            "model_loaded": self.engine.is_loaded,
        }
