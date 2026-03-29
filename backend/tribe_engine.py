"""TRIBE v2 Engine — wraps Meta's brain encoding model for content scoring."""

import time
import logging
import numpy as np
from pathlib import Path
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

# Set to True once TribeEngine.load() succeeds. External code can check this
# before calling prediction methods to avoid a hard crash when the model is not
# installed.
TRIBE_AVAILABLE: bool = False


class TribeEngine:
    """Singleton wrapper around TRIBE v2 model."""

    _instance: Optional["TribeEngine"] = None
    _model = None
    _loaded = False
    _loading = False

    @classmethod
    def get(cls) -> "TribeEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        """Load TRIBE model. Call once at startup or on first request."""
        if self._loaded or self._loading:
            return
        self._loading = True
        logger.info("Loading TRIBE v2 model...")
        start = time.time()

        try:
            try:
                from tribev2.demo_utils import TribeModel
            except ImportError:
                try:
                    from tribe.demo_utils import TribeModel
                except ImportError:
                    raise ImportError(
                        "TRIBE v2 not installed. Install from: https://github.com/facebookresearch/tribev2\n"
                        "Try: pip install git+https://github.com/facebookresearch/tribev2.git\n"
                        "Or clone the repo and: pip install -e /path/to/tribev2"
                    )
            self._model = TribeModel.from_pretrained(
                "facebook/tribev2",
                cache_folder=str(settings.tribe_cache),
            )
            self._loaded = True
            global TRIBE_AVAILABLE
            TRIBE_AVAILABLE = True
            elapsed = time.time() - start
            logger.info(f"TRIBE v2 loaded in {elapsed:.1f}s")
        except Exception as e:
            logger.error(f"Failed to load TRIBE: {e}")
            self._loading = False
            raise
        finally:
            self._loading = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict_video(self, video_path: str) -> dict:
        """Score a video file. Returns raw predictions + segments."""
        if not self._loaded:
            self.load()
        events = self._model.get_events_dataframe(video_path=video_path)
        preds, segments = self._model.predict(events=events)
        return {"predictions": preds, "segments": segments, "modality": "video"}

    def predict_audio(self, audio_path: str) -> dict:
        """Score an audio file."""
        if not self._loaded:
            self.load()
        events = self._model.get_events_dataframe(audio_path=audio_path)
        preds, segments = self._model.predict(events=events)
        return {"predictions": preds, "segments": segments, "modality": "audio"}

    def predict_text(self, text_path: str) -> dict:
        """Score a text file."""
        if not self._loaded:
            self.load()
        events = self._model.get_events_dataframe(text_path=text_path)
        preds, segments = self._model.predict(events=events)
        return {"predictions": preds, "segments": segments, "modality": "text"}

    def predict(self, file_path: str) -> dict:
        """Auto-detect modality and predict."""
        ext = Path(file_path).suffix.lower()
        if ext in (".mp4", ".avi", ".mkv", ".mov", ".webm"):
            return self.predict_video(file_path)
        elif ext in (".wav", ".mp3", ".flac", ".ogg"):
            return self.predict_audio(file_path)
        elif ext in (".txt",):
            return self.predict_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
