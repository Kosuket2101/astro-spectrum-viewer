#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FILTER_DIR = ROOT / "filters"
OUTPUT = FILTER_DIR / "index.json"
VALID_SUFFIXES = {".csv", ".txt", ".dat"}


def read_metadata(path: Path):
    """Read optional '# key: value' metadata from the beginning of a filter file."""
    meta = {}
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as f:
            for _ in range(80):
                line = f.readline()
                if not line:
                    break
                m = re.match(r"^\s*#\s*([^:]+)\s*:\s*(.+?)\s*$", line)
                if m:
                    meta[m.group(1).strip().lower()] = m.group(2).strip()
    except OSError:
        pass
    return meta


def pretty_folder_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip()


def infer_group(path: Path, meta: dict):
    """
    Preferred layout:
      filters/<Telescope>/<Instrument>/<filter-file>

    Metadata can override directory-derived names:
      # telescope: Subaru
      # instrument: HSC
      # name: g
    """
    rel_parts = path.relative_to(FILTER_DIR).parts

    if len(rel_parts) >= 3:
        telescope = pretty_folder_name(rel_parts[0])
        instrument = pretty_folder_name(rel_parts[1])
    elif len(rel_parts) == 2:
        telescope = pretty_folder_name(rel_parts[0])
        instrument = "General"
    else:
        telescope = "Other"
        instrument = "Ungrouped"

    telescope = meta.get("telescope", telescope)
    instrument = meta.get("instrument", instrument)
    return telescope, instrument


entries = []
for path in sorted(FILTER_DIR.rglob("*")):
    if not path.is_file():
        continue
    if path.name == "index.json" or path.suffix.lower() not in VALID_SUFFIXES:
        continue

    meta = read_metadata(path)
    telescope, instrument = infer_group(path, meta)
    rel = path.relative_to(ROOT).as_posix()

    # SVO ASCII transmission curves are treated as Angstrom by default.
    wavelength_unit = (
        meta.get("wavelength_unit")
        or meta.get("wave_unit")
        or meta.get("unit")
        or "angstrom"
    )

    entry = {
        "telescope": telescope,
        "instrument": instrument,
        "name": meta.get("name", path.stem),
        "path": rel,
        "wavelength_unit": wavelength_unit,
    }

    if "color" in meta:
        entry["color"] = meta["color"]
    if "svo_id" in meta:
        entry["svo_id"] = meta["svo_id"]
    if "source" in meta:
        entry["source"] = meta["source"]

    entries.append(entry)

entries.sort(key=lambda e: (
    e["telescope"].casefold(),
    e["instrument"].casefold(),
    e["name"].casefold(),
))

OUTPUT.write_text(
    json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(entries)} filters.")
