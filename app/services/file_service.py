"""
Сервис для работы с файлами.
Обеспечивает загрузку изображений в S3 и другие файловые операции.
"""
from typing import Optional, Dict, Any
from fastapi import UploadFile

from app import utils


class FileService:
    """Сервис для работы с файлами."""

    async def upload_image_to_s3(
        self,
        file: UploadFile,
        prefix: str = "uploads",
        max_size_mb: int = 10
    ) -> str:
        """Загружает изображение в S3 и возвращает URL."""
        # Проверяем расширение
        utils.validate_upload_image(file, max_size_mb)

        # Загружаем в S3
        return await utils.upload_image_to_s3(file, prefix)

    def get_s3_client(self):
        """Возвращает клиент S3."""
        return utils.s3_client

    def get_s3_bucket(self) -> str:
        """Возвращает имя бакета S3."""
        return utils.settings.S3_BUCKET
