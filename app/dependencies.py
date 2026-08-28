import json
from typing import Optional
from fastapi import Request, Cookie, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from jose import JWTError, jwt
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models import TokenData
from app.services.character_service import CharacterService
from app.services.room_service import RoomService
from app.services.combat_service import CombatService
from app.services.spell_service import SpellService
from app.services.file_service import FileService

# Инициализация шаблонизатора Jinja2
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# === Фабрики сервисов (Dependency Injection) ===

def get_character_service() -> CharacterService:
    """Возвращает экземпляр сервиса для работы с персонажами."""
    return CharacterService()

def get_room_service() -> RoomService:
    """Возвращает экземпляр сервиса для работы с комнатами."""
    return RoomService()

def get_combat_service() -> CombatService:
    """Возвращает экземпляр сервиса для работы с боем."""
    return CombatService()

def get_spell_service() -> SpellService:
    """Возвращает экземпляр сервиса для работы с заклинаниями."""
    return SpellService()

def get_file_service() -> FileService:
    """Возвращает экземпляр сервиса для работы с файлами."""
    return FileService()


# Сериализатор для криптографической подписи кук
serializer = URLSafeTimedSerializer(
    secret_key=settings.SECRET_KEY,
    salt="session-cookie-salt"
)

SESSION_MAX_AGE = 86400  # 24 часа


def sign_session_data(user_data: dict) -> str:
    """Создаёт зашифрованную и подписанную строку сессии."""
    return serializer.dumps(user_data)


def unsign_session_data(signed_session: str) -> Optional[dict]:
    """Проверяет подпись и срок действия куки."""
    try:
        data = serializer.loads(signed_session, max_age=SESSION_MAX_AGE)
        return data
    except (BadSignature, SignatureExpired, Exception):
        return None


# === Получение и проверка текущего пользователя ===

async def get_current_user(
        request: Request,
        session: Optional[str] = Cookie(default=None)
) -> dict:
    """
    Извлекает и валидирует пользователя из подписанной cookie-сессии.
    Если кука недействительна, возвращает 401 или редирект на /login (но без петли).
    """
    if not session:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"}
        )

    user_data = unsign_session_data(session)

    if not user_data or not isinstance(user_data, dict):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"}
        )

    return user_data


# === Устаревшие проверки ролей (оставляем заглушки или удаляем) ===
# Больше нет глобальных ролей 'master'/'player' у аккаунтов.
# Права Мастера теперь проверяются внутри конкретных комнат по master_id.
async def require_master(current_user: dict = Depends(get_current_user)):
    return current_user

async def require_player(current_user: dict = Depends(get_current_user)):
    return current_user


# === Проверка прав собственности и присутствия в комнатах ===

def check_character_ownership(char_id: int, username: str) -> dict:
    """Проверяет, принадлежит ли персонаж пользователю."""
    from app.utils import load_chars

    chars = load_chars(username)
    char = next((c for c in chars if c['id'] == char_id), None)

    if not char:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден или у вас нет прав на его редактирование"
        )
    return char


async def require_in_room(
        room_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Проверяет, что пользователь имеет доступ к указанной комнате (Мастер или игрок)"""
    from app.utils import get_db_connection
    import psycopg2.extras

    try:
        room_id_int = int(room_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Неверный ID комнаты")

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Ищем комнату в БД
            cur.execute("SELECT * FROM rooms WHERE id = %s", (room_id_int,))
            room = cur.fetchone()

            if not room:
                raise HTTPException(status_code=404, detail="Комната не найдена")

            # Проверяем, является ли текущий юзер создателем (мастером) этой комнаты
            if room['master_id'] == current_user['id']:
                return room

            # Проверяем, находится ли юзер в таблице участников комнаты (room_players)
            cur.execute(
                "SELECT id FROM room_players WHERE room_id = %s AND user_id = %s",
                (room_id_int, current_user['id'])
            )
            is_player = cur.fetchone()

            if not is_player:
                raise HTTPException(status_code=403, detail="Доступ запрещён")

    return room


# === JWT Авторизация для API ===

security = HTTPBearer(auto_error=False)

async def get_token_credentials(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    if credentials is None:
        return None
    return credentials.credentials


async def get_current_user_jwt(
        token: Optional[str] = Depends(get_token_credentials)
) -> TokenData:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username, role="user")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================
# === Зависимости для работы с комнатами (пункт 3.1) ===
# ============================================================

async def get_room_or_404(room_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Проверяет существование комнаты по ID. Возвращает комнату или выбрасывает 404.

    Аргументы:
        room_id: ID комнаты (строка, будет преобразована в int)
        current_user: текущий пользователь (из Depends)

    Возвращает:
        dict: данные комнаты

    Исключения:
        HTTPException 404: комната не найдена или ID неверен
    """
    from app.utils import get_db_connection
    import psycopg2.extras

    try:
        room_id_int = int(room_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Неверный ID комнаты")

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM rooms WHERE id = %s", (room_id_int,))
            room = cur.fetchone()
            if not room:
                raise HTTPException(status_code=404, detail="Комната не найдена")
            return room


async def require_room_master(room_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Проверяет, что текущий пользователь является мастером комнаты.
    Возвращает комнату или выбрасывает 403.

    Аргументы:
        room_id: ID комнаты (строка)
        current_user: текущий пользователь

    Возвращает:
        dict: данные комнаты

    Исключения:
        HTTPException 403: пользователь не является мастером
        HTTPException 404: комната не найдена
    """
    room = await get_room_or_404(room_id, current_user)
    if room['master_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Доступ запрещён: вы не мастер этой комнаты")
    return room


async def require_room_access(room_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Проверяет, что пользователь является мастером или игроком в комнате.
    Возвращает комнату или выбрасывает 403.

    Аргументы:
        room_id: ID комнаты (строка)
        current_user: текущий пользователь

    Возвращает:
        dict: данные комнаты

    Исключения:
        HTTPException 403: доступ запрещён
        HTTPException 404: комната не найдена
    """
    from app.utils import get_db_connection
    import psycopg2.extras

    room = await get_room_or_404(room_id, current_user)
    if room['master_id'] == current_user['id']:
        return room

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM room_players WHERE room_id = %s AND user_id = %s",
                (room['id'], current_user['id'])
            )
            if cur.fetchone():
                return room

    raise HTTPException(status_code=403, detail="Доступ запрещён: вы не являетесь участником комнаты")


async def get_room_player(room_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Возвращает информацию об участии пользователя в комнате.
    Возвращает словарь с ролью ('master' или 'player') и данными.

    Аргументы:
        room_id: ID комнаты (строка)
        current_user: текущий пользователь

    Возвращает:
        dict: {
            'role': 'master' | 'player',
            'room': dict,                  # данные комнаты
            'player_data': dict | None     # запись из room_players (если роль 'player')
        }

    Исключения:
        HTTPException 403: пользователь не является участником
        HTTPException 404: комната не найдена
    """
    from app.utils import get_db_connection
    import psycopg2.extras

    room = await get_room_or_404(room_id, current_user)
    if room['master_id'] == current_user['id']:
        return {"role": "master", "room": room}

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM room_players WHERE room_id = %s AND user_id = %s",
                (room['id'], current_user['id'])
            )
            player = cur.fetchone()
            if player:
                return {"role": "player", "room": room, "player_data": player}

    raise HTTPException(status_code=403, detail="Вы не являетесь участником комнаты")
