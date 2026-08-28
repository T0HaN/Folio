"""
Сервис для боевых расчётов.
Обеспечивает инициативу, урон, токены и другие боевые механики.
"""
from typing import List, Dict, Any, Optional

from app import utils


class CombatService:
    """Сервис для боевых расчётов."""

    # === Инициатива ===

    def calculate_initiative(self, char: Dict[str, Any]) -> int:
        """Рассчитывает инициативу персонажа (модификатор Ловкости + бонусы)."""
        dex_mod = char.get('stats', {}).get('DEX', {}).get('modifier', 0)
        # TODO: добавить бонусы от черт и предметов
        return dex_mod

    def roll_initiative(self, char: Dict[str, Any]) -> int:
        """Совершает бросок инициативы."""
        import random
        return random.randint(1, 20) + self.calculate_initiative(char)

    # === Урон ===

    def parse_damage(self, damage_str: str) -> Dict[str, Any]:
        """Парсит строку урона (например, '2d6+3')."""
        return utils.parse_damage(damage_str)

    def roll_damage(self, damage_str: str) -> int:
        """Совершает бросок урона по строке."""
        import random
        parsed = self.parse_damage(damage_str)
        if not parsed:
            return 0

        total = 0
        for _ in range(parsed.get('num_dice', 1)):
            total += random.randint(1, parsed.get('die_size', 6))
        total += parsed.get('bonus', 0)
        return max(0, total)

    def calculate_damage_with_modifiers(
        self,
        damage_str: str,
        stat_modifier: int = 0,
        proficiency_bonus: int = 0,
        is_critical: bool = False
    ) -> int:
        """Рассчитывает урон с учётом модификаторов и крита."""
        import random
        parsed = self.parse_damage(damage_str)
        if not parsed:
            return 0

        num_dice = parsed.get('num_dice', 1)
        die_size = parsed.get('die_size', 6)
        bonus = parsed.get('bonus', 0)

        if is_critical:
            num_dice *= 2

        total = 0
        for _ in range(num_dice):
            total += random.randint(1, die_size)

        total += bonus + stat_modifier + proficiency_bonus
        return max(0, total)

    # === Токены ===

    def generate_token_id(self) -> str:
        """Генерирует уникальный ID для токена."""
        import uuid
        return str(uuid.uuid4())[:8]

    def create_token(
        self,
        name: str,
        x: int = 0,
        y: int = 0,
        width: int = 50,
        height: int = 50,
        image_url: Optional[str] = None,
        hp_current: int = 10,
        hp_max: int = 10,
        is_player: bool = True,
        char_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Создаёт новый токен."""
        return {
            'id': self.generate_token_id(),
            'name': name,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'image_url': image_url,
            'hp_current': hp_current,
            'hp_max': hp_max,
            'is_player': is_player,
            'char_id': char_id
        }

    # === Боевые расчёты (обёртки над utils) ===

    def get_combat_round_state(self, room_state: Dict[str, Any]) -> Dict[str, Any]:
        """Возвращает текущее состояние боя из состояния комнаты."""
        return {
            'combatants': room_state.get('combatants', []),
            'turn_index': room_state.get('turn_index', 0),
            'is_combat_active': room_state.get('is_combat_active', False)
        }

    def get_monsters(self) -> List[Dict[str, Any]]:
        """Возвращает список всех монстров."""
        return utils.get_all_monsters()
