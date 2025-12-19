import json
from collections import OrderedDict
from pathlib import Path

# --------------------------------
# BASE PATHS (ONLY CHANGE)
# --------------------------------

INITIAL_JSON_DIR = Path("../../data_nsw/initial_json")
FINAL_JSON_DIR = Path("../../data_nsw/final_json")

FINAL_JSON_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------
# PROCESS EACH INITIAL JSON FOLDER
# --------------------------------

for act_dir in INITIAL_JSON_DIR.iterdir():
    if not act_dir.is_dir():
        continue

    INPUT_JSON = act_dir / "rag_chunks.json"
    if not INPUT_JSON.exists():
        continue

    output_dir = FINAL_JSON_DIR / act_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)

    OUTPUT_JSON = output_dir / "rag_chunks_merged.json"

    # --------------------------------
    # LOAD INPUT
    # --------------------------------

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # --------------------------------
    # GROUP + MERGE (UNCHANGED)
    # --------------------------------

    merged = OrderedDict()

    for chunk in chunks:
        meta = chunk["metadata"]

        key = (
            meta.get("act"),
            meta.get("section"),
            meta.get("heading"),
            meta.get("part"),
            meta.get("division"),
            meta.get("subdivision"),
        )

        if key not in merged:
            merged[key] = {
                "id": chunk["id"].split("(")[0],
                "text_parts": [],
                "metadata": meta
            }

        merged[key]["text_parts"].append(chunk["text"])

    # --------------------------------
    # FINALIZE OUTPUT
    # --------------------------------

    final_chunks = []

    for data in merged.values():
        final_chunks.append({
            "id": data["id"],
            "text": " ".join(data["text_parts"]),
            "metadata": data["metadata"]
        })

    # --------------------------------
    # WRITE OUTPUT
    # --------------------------------

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ {act_dir.name}: Merged {len(chunks)} → {len(final_chunks)} chunks")
