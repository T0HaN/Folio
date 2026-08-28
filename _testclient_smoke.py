# -*- coding: utf-8 -*-
"""Полный авторизованный смоук через TestClient (рендер реальных страниц)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient

from app.main import app

cookie = Path("cookie.txt").read_text(encoding="utf-8").strip()

checks = [
    ("/games", "Мои кампании"),
    ("/chars", "Ваши Герои"),
    ("/char/1", "Лист персонажа"),
]

failed = False
with TestClient(app, follow_redirects=False) as client:
    client.cookies.set("session", cookie)
    for path, marker in checks:
        r = client.get(path)
        ok = r.status_code == 200 and marker in r.text
        if not ok:
            failed = True
        print(f"{'PASS' if ok else 'FAIL'}  {path}  HTTP={r.status_code}  marker='{marker}': {marker in r.text}  bytes={len(r.text)}")

print("\nTESTCLIENT_SMOKE_" + ("FAILED" if failed else "PASSED"))
