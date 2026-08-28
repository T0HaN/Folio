# -*- coding: utf-8 -*-
"""Временный смоук-тест: компиляция и рендер новых pages/* шаблонов."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TPL = Path(__file__).parent / "app" / "templates"
env = Environment(
    loader=FileSystemLoader(str(TPL)),
    autoescape=True,
)


class FakeRequest:
    def __init__(self, path):
        self.url = type("U", (), {"path": path})()


env.globals["url_for"] = lambda name, **kw: "/static/" + (kw.get("path", "") or "")
env.globals["request"] = FakeRequest("/char/1")


def render(name, ctx):
    tmpl = env.get_template(name)
    html = tmpl.render(**ctx)
    print(f"OK  {name}  -> {len(html)} bytes")
    return html


# ---------- mock-данные персонажа ----------
char = {
    "id": 1,
    "name": "Тестовый Воин",
    "level": 3,
    "xp": 900,
    "char_class": "Воин",
    "subclass": "Нет",
    "race": "Человек",
    "alignment": "Законно-нейтральный",
    "physical": {"height": "180 см", "weight": "80 кг", "hair": "Тёмные", "eyes": "Карие"},
    "stats": {
        "STR": {"score": 16, "modifier": 3},
        "DEX": {"score": 14, "modifier": 2},
        "CON": {"score": 15, "modifier": 2},
        "INT": {"score": 10, "modifier": 0},
        "WIS": {"score": 12, "modifier": 1},
        "CHA": {"score": 8, "modifier": -1},
    },
    "saving_throws": ["Сила"],
    "skills": ["Атлетика"],
    "attributes": {"initiative": 2, "speed": 30, "prof_bonus": "+2"},
    "hp": {"current": 25, "max": 30, "temp": 5},
    "inventory": {
        "weapons": [
            {"name": "Длинный меч", "damage": "1к8", "proficient": True, "type": "standard", "description": "Рубящее"},
            {"name": "Кинжал", "damage": "1к4", "proficient": True, "type": "finesse", "description": ""},
        ],
        "armor": [
            {"name": "Кольчуга", "ac": "16", "equipped": True, "strength_req": "Сил 13", "stealth": "Помеха"},
        ],
        "gear": [],
        "arrows": [],
        "bolts": [],
        "coins": {"cp": 0, "sp": 0, "ep": 0, "gp": 5, "pp": 0},
        "known_spells": [],
    },
    "_calculated_ac": 16,
    "_carry": {
        "max_capacity": 240, "push_drag_lift": 480, "current_weight": 55,
        "encumbrance_level": 0, "encumbrance_name": "Свободен", "speed_penalty": 0,
        "thresholds": {"light": 80, "medium": 160, "heavy": 240, "max": 480},
    },
    "token_image": None,
}

saves = [
    {"name": "Сила", "abbr": "Сил", "mod": 3, "proficient": True, "total": 5},
    {"name": "Ловкость", "abbr": "Лов", "mod": 2, "proficient": False, "total": 2},
    {"name": "Телосложение", "abbr": "Тел", "mod": 2, "proficient": False, "total": 2},
    {"name": "Интеллект", "abbr": "Инт", "mod": 0, "proficient": False, "total": 0},
    {"name": "Мудрость", "abbr": "Мдр", "mod": 1, "proficient": False, "total": 1},
    {"name": "Харизма", "abbr": "Хар", "mod": -1, "proficient": False, "total": -1},
]
skills = [
    {"name": "Атлетика", "abbr": "Сил", "mod": 3, "proficient": True, "total": 5},
    {"name": "Скрытность", "abbr": "Лов", "mod": 2, "proficient": False, "total": 2},
    {"name": "Внимательность", "abbr": "Мдр", "mod": 1, "proficient": False, "total": 1},
]

# ---------- рендер ----------
render("pages/character.html", {
    "char": char,
    "saves": saves,
    "skills": skills,
    "class_features": [],
    "back_url": "/chars",
    "back_text": "← Назад к списку",
    "current_user": {"username": "test", "role": "player"},
    "xp_progress": 50.0,
    "next_level_xp": 2700,
})

render("pages/characters.html", {
    "chars": [char],
    "username": "test",
    "role": "player",
    "quote_text": "Цитата",
    "error": None,
    "success": None,
    "info": None,
})

room = {"id": 1, "name": "Проклятие Страда", "active": True, "max_players": 5, "invite_code": "AB3XY9"}
render("pages/games.html", {
    "master_rooms": [room],
    "player_rooms": [{"id": 2, "name": "Страд", "active": True, "char_name": "Воин"}],
    "chars": [char],
    "current_user": {"username": "test", "id": 1, "role": "player"},
    "quote_text": "Цитата",
    "error": None,
    "success": None,
    "info": None,
})

print("\nSMOKE_TEST_PASSED")
