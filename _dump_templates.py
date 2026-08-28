# Вспомогательный скрипт для дампа шаблонов в UTF-8 файлы (для миграции).
# Временный; будет удалён после завершения миграции.
import os
from pathlib import Path

BASE = Path(r"c:\Users\MBOU SOSH 29\Documents\GitHub\Folio")
TPL = BASE / "app" / "templates"
OUT = BASE / "_dump_tmp"
OUT.mkdir(exist_ok=True)

files = ["games.html", "CharList1.html", "character_view.html"]
for name in files:
    src = TPL / name
    dst = OUT / name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{name}: {src.stat().st_size} bytes -> {dst}")

# Также выведем размеры остальных нужных файлов
for p in [TPL / "base" / "base.html",
          TPL / "pages" / "dashboard.html",
          TPL / "pages" / "login.html",
          TPL / "components" / "card.html",
          TPL / "components" / "modal.html",
          TPL / "components" / "sidebar.html",
          TPL / "components" / "header.html",
          TPL / "partials" / "flash_messages.html"]:
    if p.exists():
        print(f"{p.relative_to(BASE)}: {p.stat().st_size} bytes")
    else:
        print(f"{p.relative_to(BASE)}: MISSING")

# Список css/js
for root in [BASE / "app" / "static" / "css", BASE / "app" / "static" / "js"]:
    print(f"\n--- {root.relative_to(BASE)} ---")
    for dirpath, _dirs, files_ in os.walk(root):
        for f in sorted(files_):
            rel = Path(dirpath).relative_to(BASE)
            print(f"  {rel / f}  ({Path(dirpath, f).stat().st_size} bytes)")
