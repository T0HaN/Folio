from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # === JWT / AUTH ===
    # ============================================================
    # Секреты задаются через переменные окружения / .env (см. .env.example),
    # реальные значения в коде не хранятся.
    SECRET_KEY: str = Field(..., description="Секретный ключ для подписи кук сессий и JWT. Обязателен!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа

    # ============================================================
    # === DIRECTORIES ===
    # ============================================================
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"

    # ============================================================
    # === STATIC DATA (JSON files) ===
    # ============================================================
    # Справочники остаются в JSON, так как они редко меняются и не требуют реляционных связей
    CLASSES_DIR: Path = DATA_DIR / "classes"       # Папка с JSON-файлами классов
    EQUIPMENT_FILE: Path = DATA_DIR / "equipment.json"
    SPELLS_FILE: Path = DATA_DIR / "spells.json"

    # ============================================================
    # === POSTGRESQL DATABASE ===
    # ============================================================
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "dnd"
    DB_USER: str = "dndapp"
    DB_PASSWORD: str = Field(..., description="Пароль от БД PostgreSQL. Обязателен!")

    # ============================================================
    # === REDIS DATABASE ===
    # ============================================================
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # ============================================================
    # === S3 / MinIO Settings ===
    # ============================================================
    S3_ENDPOINT: str = "http://127.0.0.1:9000"
    S3_ACCESS_KEY: str = Field(..., description="Ключ доступа к S3/MinIO. Обязателен!")
    S3_SECRET_KEY: str = Field(..., description="Секретный ключ S3/MinIO. Обязателен!")
    S3_BUCKET: str = "folio-maps"

    # ============================================================
    # === CORS ===
    # ============================================================
    # Список разрешённых источников через запятую (например, http://localhost:3000)
    CORS_ORIGINS: str = "http://localhost:8000"

    # ============================================================
    # === ЛИМИТЫ ЗАГРУЗКИ ФАЙЛОВ ===
    # ============================================================
    MAX_UPLOAD_SIZE_MB: int = 5  # Максимальный размер загружаемого файла, МБ

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()

settings.DATA_DIR.mkdir(exist_ok=True)
(settings.DATA_DIR / "user_data").mkdir(exist_ok=True)
