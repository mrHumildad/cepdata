import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Writes the server-local station seed list consumed by aggregate.py and
# mcsc_sample.py. The client app also needs the same list — mirror it into the
# client repo as src/logic/stations.json (see README).
META = SCRIPT_DIR / "meta.json"
OUT = SCRIPT_DIR.parent / "config" / "stations.json"

meta = json.loads(META.read_text(encoding="utf-8"))

result = []
for codi, info in meta.items():
    entry = {
        "codi": codi,
        "nom": info.get("nom"),
        "altitud": info.get("altitud"),
        "comarca": info.get("comarca", {}).get("nom"),
        "coordenades": info.get("coordenades")
    }
    result.append(entry)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(f"Extracted {len(result)} entries to {OUT}")
