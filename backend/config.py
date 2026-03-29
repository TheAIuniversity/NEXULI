from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tribe_cache: Path = Path("./cache")
    tribe_device: str = "auto"  # "auto", "cpu", "cuda", "mps"
    upload_dir: Path = Path("./uploads")
    db_path: Path = Path("./data/tribe.db")
    vault_path: Path = Path("../vault")
    host: str = "0.0.0.0"
    port: int = 8100

    class Config:
        env_prefix = "TRIBE_"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.tribe_cache.mkdir(parents=True, exist_ok=True)
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
