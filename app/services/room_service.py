"""
Сервис для управления комнатами.
Обеспечивает создание, удаление, доступ и управление игроками в комнатах.
"""
from typing import List, Dict, Any, Optional

from app import utils
from app.repositories.room_repository import RoomRepository
from app.repositories.character_repository import CharacterRepository


class RoomService:
    """Сервис для управления комнатами."""

    def __init__(self):
        self.room_repo = RoomRepository()
        self.char_repo = CharacterRepository()

    # === Основные операции с комнатами ===

    def load_rooms(self) -> Dict[str, Any]:
        """Загружает все комнаты."""
        return self.room_repo.load_rooms()

    def save_rooms(self, data: Dict[str, Any]) -> None:
        """Сохраняет данные комнат."""
        return self.room_repo.save_rooms(data)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает комнату по ID."""
        return self.room_repo.get_room(room_id)

    def get_room_by_invite_code(self, invite_code: str) -> Optional[Dict[str, Any]]:
        """Возвращает комнату по коду приглашения."""
        return self.room_repo.get_room_by_invite_code(invite_code)

    def create_room(self, master_id: int, name: str, description: str = "", max_players: int = 6) -> Dict[str, Any]:
        """Создаёт новую комнату."""
        rooms_data = self.load_rooms()
        rooms = rooms_data.get('rooms', [])

        import time
        new_id = int(time.time() * 1000) % 1000000

        import random
        import string
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        new_room = {
            'id': new_id,
            'name': name,
            'description': description,
            'master_id': master_id,
            'invite_code': invite_code,
            'max_players': max_players,
            'active': True,
            'created_at': time.time(),
            'current_players': []
        }

        rooms.append(new_room)
        self.save_rooms({'rooms': rooms})
        return new_room

    def delete_room(self, room_id: int, master_id: int) -> bool:
        """Удаляет комнату, если пользователь является мастером."""
        rooms_data = self.load_rooms()
        rooms = rooms_data.get('rooms', [])
        room = next((r for r in rooms if r.get('id') == room_id), None)

        if not room or room.get('master_id') != master_id:
            return False

        rooms = [r for r in rooms if r.get('id') != room_id]
        self.save_rooms({'rooms': rooms})
        return True

    # === Управление игроками в комнате ===

    def add_player_to_room(self, room_id: int, user_id: int, char_id: int, char_name: str) -> bool:
        """Добавляет игрока в комнату."""
        rooms_data = self.load_rooms()
        rooms = rooms_data.get('rooms', [])
        room = next((r for r in rooms if r.get('id') == room_id), None)

        if not room:
            return False

        current_players = room.get('current_players', [])
        if len(current_players) >= room.get('max_players', 6):
            return False

        if any(p.get('user_id') == user_id for p in current_players):
            return True  # Уже есть

        current_players.append({
            'user_id': user_id,
            'character_id': char_id,
            'char_name': char_name,
            'joined_at': time.time()
        })

        room['current_players'] = current_players
        self.save_rooms({'rooms': rooms})
        return True

    def remove_player_from_room(self, room_id: int, user_id: int) -> bool:
        """Удаляет игрока из комнаты."""
        rooms_data = self.load_rooms()
        rooms = rooms_data.get('rooms', [])
        room = next((r for r in rooms if r.get('id') == room_id), None)

        if not room:
            return False

        current_players = room.get('current_players', [])
        current_players = [p for p in current_players if p.get('user_id') != user_id]
        room['current_players'] = current_players
        self.save_rooms({'rooms': rooms})
        return True

    def is_user_in_room(self, room_id: int, user_id: int) -> bool:
        """Проверяет, находится ли пользователь в комнате."""
        room = self.get_room(room_id)
        if not room:
            return False
        return any(p.get('user_id') == user_id for p in room.get('current_players', []))

    def is_user_master(self, room_id: int, user_id: int) -> bool:
        """Проверяет, является ли пользователь мастером комнаты."""
        room = self.get_room(room_id)
        if not room:
            return False
        return room.get('master_id') == user_id


    # === Сцены (обёртка над utils) ===

    def get_room_scenes(self, room_id: int) -> list:
        """Возвращает список сцен комнаты."""
        return utils.get_room_scenes(room_id)

    def create_scene(self, room_id: int, name: str, background_url: str, width: int, height: int) -> dict:
        """Создаёт новую сцену."""
        return utils.create_scene(room_id, name, background_url, width, height)

    def set_active_scene(self, room_id: int, scene_id: int) -> None:
        """Устанавливает активную сцену."""
        return utils.set_active_scene(room_id, scene_id)

    def delete_scene(self, room_id: int, scene_id: int) -> dict:
        """Удаляет сцену."""
        return utils.delete_scene(room_id, scene_id)

    # === Redis состояние ===

    async def get_redis_room_state(self, room_id: str) -> dict:
        """Получает состояние комнаты из Redis."""
        return await utils.get_redis_room_state(room_id)

    async def save_redis_room_state(self, room_id: str, state: dict) -> None:
        """Сохраняет состояние комнаты в Redis."""
        return await utils.save_redis_room_state(room_id, state)

    # === История игрока ===

    def add_room_to_player_history(self, username: str, room_id: str) -> None:
        """Добавляет комнату в историю игрока."""
        return self.room_repo.add_room_to_player_history(username, room_id)

    def cleanup_inactive_players(self, room_id: str, timeout: int = 30) -> None:
        """Удаляет неактивных игроков."""
        return self.room_repo.cleanup_inactive_players(room_id, timeout)
