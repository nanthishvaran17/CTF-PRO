from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CTFX_", env_file=".env", extra="ignore")

    APP_NAME: str = "CTF HUNTER X"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Mode: LOCAL (no auth, loopback only) or REMOTE (auth, sessions, CSRF, rate-limit, audit)
    MODE: str = Field(default="LOCAL", description="LOCAL or REMOTE")
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Security & Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    STORAGE_DIR: Path = DATA_DIR / "uploads"
    ARTIFACTS_DIR: Path = DATA_DIR / "artifacts"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    PLUGINS_DIR: Path = BASE_DIR / "plugins"

    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-ctfx-hunter-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Limits
    MAX_UPLOAD_SIZE_BYTES: int = 500 * 1024 * 1024  # 500MB
    MAX_UNCOMPRESSED_SIZE_BYTES: int = 250 * 1024 * 1024  # 250MB
    MAX_ARCHIVE_FILE_COUNT: int = 2000
    MAX_ARCHIVE_RATIO: float = 100.0
    MAX_DECODE_DEPTH: int = 8
    MAX_DECODE_BUFFER_BYTES: int = 10 * 1024 * 1024  # 10MB

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'ctfx.db'}"

    def ensure_directories(self) -> None:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
