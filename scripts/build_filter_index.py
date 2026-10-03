#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FILTER_DIR = ROOT / "filters"
OUTPUT = FILTER_DIR / "index.json"
VALID_SUFFIXES = {".csv", ".txt", ".dat"}


def read_metadata(path: Path):
    meta = {}
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as f:
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                m = re.match(r"^\s*#\s*([^:]+)\s*:\s*(.+?)\s*$", line)
                if m:
                    meta[m.group(1).strip().lower()] = m.group(2).strip()
                elif line.strip() and not line.lstrip().startswith("#"):
                    break
    except OSError:
        pass
    return meta


entries = []
for path in sorted(FILTER_DIR.rglob("*")):
    if not path.is_file():
        continue
    if path.name == "index.json" or path.suffix.lower() not in VALID_SUFFIXES:
        continue

    meta = read_metadata(path)
    rel = path.relative_to(ROOT).as_posix()
    entry = {
        "name": meta.get("name", path.stem),
        "path": rel,
        "wavelength_unit": meta.get("wavelength_unit", "nm"),
    }
    if "color" in meta:
        entry["color"] = meta["color"]
    entries.append(entry)

OUTPUT.write_text(
    json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(entries)} filters.")
