"""
Репозиторий для работы с пользователями.
Обеспечивает поиск и создание пользователей через функции utils.
"""
from typing import Optional, Dict, Any

from app import utils


class UserRepository:
    """Репозиторий для доступа к данным пользователей."""

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Возвращает пользователя по имени."""
        return utils.get_user_by_username(username)

    def create_user(self, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """Создаёт нового пользователя."""
        return utils.create_user(username, password_hash)
