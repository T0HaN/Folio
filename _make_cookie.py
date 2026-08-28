# -*- coding: utf-8 -*-
"""Генерирует сессионную куку для первого персонажа в БД -> cookie.txt"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import psycopg2

from app.config import settings
from app.dependencies import sign_session_data

conn = psycopg2.connect(
    host=settings.DB_HOST, port=settings.DB_PORT, dbname=settings.DB_NAME,
    user=settings.DB_USER, password=settings.DB_PASSWORD,
)
cur = conn.cursor()
cur.execute("SELECT c.id, c.name, c.user_id FROM characters c ORDER BY c.id LIMIT 1")
row = cur.fetchone()
char_id, char_name, uid = row[0], row[1], row[2]
cur.execute("SELECT username FROM users WHERE id = %s", (uid,))
uname_row = cur.fetchone()
owner = uname_row[0] if uname_row else "unknown"
cur.close()
conn.close()

signed = sign_session_data({"id": uid, "username": owner})
Path("cookie.txt").write_text(signed, encoding="utf-8")
Path("char_meta.txt").write_text(f"{char_id}\n{char_name}", encoding="utf-8")
print(f"COOKIE_OK user={owner} uid={uid} char_id={char_id} char_name={char_name}")
