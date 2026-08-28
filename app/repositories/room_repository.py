"""
Репозиторий для работы с комнатами.
Обеспечивает загрузку, сохранение и поиск комнат через функции utils.
"""
from typing import List, Dict, Any, Optional

from app import utils


class RoomRepository:
    """Репозиторий для доступа к данным комнат."""

    def load_rooms(self) -> Dict[str, Any]:
        """Загружает все комнаты."""
        return utils.load_rooms()

    def save_rooms(self, data: Dict[str, Any]) -> None:
        """Сохраняет данные комнат."""
        return utils.save_rooms(data)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает комнату по ID."""
        rooms_data = self.load_rooms()
        for room in rooms_data.get('rooms', []):
            if room.get('id') == room_id:
                return room
        return None

    def get_room_by_invite_code(self, invite_code: str) -> Optional[Dict[str, Any]]:
        """Возвращает комнату по коду приглашения."""
        rooms_data = self.load_rooms()
        for room in rooms_data.get('rooms', []):
            if room.get('invite_code') == invite_code:
                return room
        return None

    def add_room_to_player_history(self, username: str, room_id: str) -> None:
        """Добавляет комнату в историю игрока."""
        return utils.add_room_to_player_history(username, room_id)

    def cleanup_inactive_players(self, room_id: str, timeout: int = 30) -> None:
        """Удаляет неактивных игроков из комнаты."""
        return utils.cleanup_inactive_players(room_id, timeout)
