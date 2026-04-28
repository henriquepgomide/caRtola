"""Update the README's title with the year-range available under ``data/01_raw/``."""

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
since = "9999"
until = "0000"
for entry in (ROOT / "data/01_raw/").iterdir():
    name = entry.name
    if not re.match(r"\b\d{4}\b", name):
        continue
    if name < since:
        since = name
    elif name > until:
        until = name

readme_path = ROOT / "README.md"
with readme_path.open(encoding="utf-8", errors="replace") as file:
    readme = file.readlines()
    readme[0] = f"# 🎩 CaRtola FC: Ciência de Dados e Futebol desde {since} até {until}\n"

with readme_path.open("w", encoding="utf-8", errors="replace") as file:
    file.writelines(readme)
