"""
Репозиторий для работы с персонажами.
Обеспечивает загрузку, сохранение и поиск персонажей через функции utils.
"""
from typing import List, Dict, Any, Optional

from app import utils


class CharacterRepository:
    """Репозиторий для доступа к данным персонажей."""

    def load_chars(self, username: str) -> List[Dict[str, Any]]:
        """Загружает список персонажей пользователя."""
        return utils.load_chars(username)

    def save_chars(self, username: str, chars: List[Dict[str, Any]]) -> None:
        """Сохраняет список персонажей пользователя."""
        return utils.save_chars(username, chars)

    def get_char(self, username: str, char_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает персонажа по ID."""
        for char in self.load_chars(username):
            if char.get('id') == char_id:
                return char
        return None

    def recalc_char(self, char: Dict[str, Any]) -> Dict[str, Any]:
        """Пересчитывает производные характеристики персонажа."""
        return utils.recalc_char(char)

    def normalize_char(self, char: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализует структуру персонажа."""
        return utils.normalize_char(char)
