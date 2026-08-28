"""
Сервис для работы с персонажами.

Обеспечивает загрузку, сохранение, нормализацию и валидацию данных персонажей.
"""

from typing import List, Dict, Any, Optional

from app import utils


class CharacterService:
    """Сервис для управления персонажами."""

    def load_chars(self, username: str) -> List[Dict[str, Any]]:
        """Загружает список персонажей пользователя."""
        return utils.load_chars(username)

    def save_chars(self, username: str, chars: List[Dict[str, Any]]) -> None:
        """Сохраняет список персонажей пользователя."""
        return utils.save_chars(username, chars)

    def get_char(self, username: str, char_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает одного персонажа по ID."""
        for char in self.load_chars(username):
            if char.get('id') == char_id:
                return char
        return None

    def normalize_char(self, char: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализует структуру персонажа."""
        return utils.normalize_char(char)

    def recalc_char(self, char: Dict[str, Any]) -> Dict[str, Any]:
        """Пересчитывает все производные характеристики персонажа."""
        return utils.recalc_char(char)

    def calculate_ac(self, char: Dict[str, Any]) -> int:
        """Рассчитывает Класс Доспеха персонажа."""
        return utils.calculate_ac(char)

    def prepare_skills_and_saves(self, char: Dict[str, Any]) -> Dict[str, Any]:
        """Подготавливает навыки и спасброски с учётом модификаторов."""
        return utils.prepare_skills_and_saves(char)

    def calc_modifier(self, score: int) -> int:
        """Рассчитывает модификатор характеристики."""
        return utils.calc_modifier(score)

    def calc_prof_bonus(self, level: int) -> int:
        """Рассчитывает бонус мастерства по уровню."""
        return utils.calc_prof_bonus(level)

    def calc_level_from_xp(self, xp: int) -> int:
        """Рассчитывает уровень по опыту."""
        return utils.calc_level_from_xp(xp)

    def get_level_progress(self, xp: int, level: int) -> float:
        """Возвращает прогресс уровня в процентах."""
        return utils.get_level_progress(xp, level)

    def get_class_features(self, char_class: str, subclass: str, level: int) -> List[Dict[str, Any]]:
        """Возвращает список умений класса для указанного уровня."""
        return utils.get_class_features(char_class, subclass, level)

    def get_spells_for_class(
        self,
        char_class: str,
        char_level: int,
        known_spells: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Возвращает список заклинаний для класса."""
        return utils.get_spells_for_class(char_class, char_level, known_spells or [])

    def parse_damage(self, damage_str: str) -> Dict[str, Any]:
        """Парсит строку урона."""
        return utils.parse_damage(damage_str)

    def map_weapon_type(self, weapon_name: str) -> str:
        """Определяет тип оружия."""
        return utils.map_weapon_type(weapon_name)

    def determine_weapon_proficiency(
        self,
        char_class: str,
        weapon_category: str,
        weapon_name: str
    ) -> bool:
        """Определяет владение оружием."""
        return utils.determine_weapon_proficiency(char_class, weapon_category, weapon_name)

    def calculate_total_weight(self, char: Dict[str, Any]) -> float:
        """Рассчитывает общий вес инвентаря."""
        return utils.calculate_total_weight(char)

    def calculate_carry_capacity(self, char: Dict[str, Any]) -> dict:
        """Рассчитывает грузоподъёмность персонажа."""
        return utils.calculate_carry_capacity(char)
