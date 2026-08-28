# Временный скрипт для извлечения средних частей шаблонов
import os
from pathlib import Path

BASE = Path(r"c:\Users\MBOU SOSH 29\Documents\GitHub\Folio")
DUMP_DIR = BASE / "_dump_tmp"
DUMP_DIR.mkdir(exist_ok=True)

def extract_range(src_name, start, end, dst_name):
    src = DUMP_DIR / src_name
    dst = DUMP_DIR / dst_name
    lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
    chunk = lines[start:end]  # end is exclusive
    dst.write_text("".join(chunk), encoding="utf-8")
    print(f"{dst_name}: {len(chunk)} lines")

# games.html: body between sidebar and modals
extract_range("games.html", 83, 283, "games_mid.html")  # lines 84-283 (0-indexed: 83..282)

# CharList1.html: body between header and footer/sidebar
extract_range("CharList1.html", 87, 322, "cl1_mid.html")  # lines 88-321

# character_view.html: split into 3 chunks of ~2000 lines
src = DUMP_DIR / "character_view.html"
lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
total = len(lines)
print(f"character_view.html total lines: {total}")
chunk_size = 2000
for i in range(0, total, chunk_size):
    chunk = lines[i:i+chunk_size]
    dst = DUMP_DIR / f"cv_chunk_{i//chunk_size+1}.html"
    dst.write_text("".join(chunk), encoding="utf-8")
    print(f"{dst.name}: {len(chunk)} lines")

print("Done.")
