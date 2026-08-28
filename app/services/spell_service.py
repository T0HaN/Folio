"""
Сервис для работы с заклинаниями.
Обеспечивает получение, фильтрацию и управление заклинаниями.
"""
from typing import List, Dict, Any, Optional

from app import utils


class SpellService:
    """Сервис для работы с заклинаниями."""

    def get_all_spells(self) -> List[Dict[str, Any]]:
        """Возвращает список всех заклинаний из БД."""
        return utils.get_all_spells()

    def get_spells_for_class(
        self,
        char_class: str,
        char_level: int,
        known_spells: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Возвращает список заклинаний для класса и уровня."""
        return utils.get_spells_for_class(char_class, char_level, known_spells or [])

    def filter_spells_by_level(self, spells: List[Dict[str, Any]], level: int) -> List[Dict[str, Any]]:
        """Фильтрует заклинания по уровню."""
        return [s for s in spells if s.get('level', 0) == level]

    def filter_spells_by_school(self, spells: List[Dict[str, Any]], school: str) -> List[Dict[str, Any]]:
        """Фильтрует заклинания по школе магии."""
        return [s for s in spells if s.get('school', '').lower() == school.lower()]

    def filter_spells_by_class(self, spells: List[Dict[str, Any]], char_class: str) -> List[Dict[str, Any]]:
        """Фильтрует заклинания по классу."""
        return [s for s in spells if char_class.lower() in [c.lower() for c in s.get('classes', [])]]

    def get_spell_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Возвращает заклинание по имени."""
        all_spells = self.get_all_spells()
        for spell in all_spells:
            if spell.get('name_ru', '').lower() == name.lower() or spell.get('name_en', '').lower() == name.lower():
                return spell
        return None

    def get_spells_by_names(self, names: List[str]) -> List[Dict[str, Any]]:
        """Возвращает заклинания по списку имён."""
        all_spells = self.get_all_spells()
        result = []
        for spell in all_spells:
            if spell.get('name_ru') in names or spell.get('name_en') in names:
                result.append(spell)
        return result

    def get_known_spell_names(self, char: Dict[str, Any]) -> List[str]:
        """Возвращает список имён известных заклинаний персонажа."""
        return char.get('inventory', {}).get('known_spells', [])

    def add_known_spell(self, char: Dict[str, Any], spell_name: str) -> None:
        """Добавляет заклинание в список известных."""
        char.setdefault('inventory', {}).setdefault('known_spells', [])
        if spell_name not in char['inventory']['known_spells']:
            char['inventory']['known_spells'].append(spell_name)

    def remove_known_spell(self, char: Dict[str, Any], spell_name: str) -> None:
        """Удаляет заклинание из списка известных."""
        char.setdefault('inventory', {}).setdefault('known_spells', [])
        if spell_name in char['inventory']['known_spells']:
            char['inventory']['known_spells'].remove(spell_name)

    def is_spellcaster(self, char_class: str) -> bool:
        """Проверяет, является ли класс заклинателем."""
        caster_classes = [
            'Волшебник', 'Жрец', 'Бард', 'Колдун', 'Чародей',
            'Друид', 'Паладин', 'Следопыт', 'Изобретатель'
        ]
        return char_class in caster_classes
