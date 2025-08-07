import os
import re
from pathlib import Path


ROOT = Path(__file__).parents[2]
since = '9999'
until = '0000'
for path in os.listdir(ROOT / "data/01_raw/"): 
    if not re.match(r"\b\d{4}\b", path):
        continue 
    if path < since:
        since = path
    elif path > until:
        until = path
    
with open(ROOT / "README.md", 'r', encoding="utf-8", errors="replace") as file:
    readme = file.readlines()
    readme[0] = f"# 🎩 CaRtola FC: Ciência de Dados e Futebol desde {since} até {until}\n"

with open(ROOT / "README.md", 'w', encoding="utf-8", errors="replace") as file:
    file.writelines(readme)
