from utils.qwen3b_summary import summarize
from pathlib import Path
import json
import torch

# -----------------------------
# System prompt (retrieval-focused)
# -----------------------------

SYSTEM_PROMPT = """
You generate retrieval-oriented legal summaries.

Focus on:
- regulatory scope
- administering authorities
- powers and functions
- types of obligations and regulations

Do NOT restate headings.
Do NOT include procedural detail.
Write 4–6 sentences maximum.
"""

# -----------------------------
# File iteration
# -----------------------------

def iter_json_files(root_folder):
    root = Path(root_folder)
    for json_file in root.glob("*.json"):
        yield json_file   # CHANGED: yield only the file path


def save_output(doc_id, json_path, record, out_root):
    out_dir = Path(out_root) / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / json_path.name

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

# -----------------------------
# Core processing (ONE file)
# -----------------------------

def process_file(json_path, out_root):   # CHANGED: removed doc_id param
    with open(json_path, "r", encoding="utf-8") as f:
        record = json.load(f)
        # record = records[0]

    # CHANGED: doc_id now comes from JSON
    doc_id = record.get("doc_id")

    if not doc_id:
        raise ValueError(f"Missing doc_id in {json_path}")

    jurisdiction = record.get("jurisdiction")
    act = record.get("act")
    act_headings = record.get("act_headings", [])
    country = record.get("country")

    print(f"Summarizing Act: {act}")

    summary_text = summarize(
        jurisdiction=jurisdiction,
        act=act,
        act_headings=act_headings,
        system_prompt=SYSTEM_PROMPT
    )

    record["act_retrieval_summary"] = summary_text

    save_output(doc_id, json_path, record, out_root)

    torch.cuda.empty_cache()

    return record


def run(root_folder, out_root):
    for json_path in iter_json_files(root_folder):   # CHANGED
        print(f"Processing {json_path}")
        process_file(json_path, out_root)            # CHANGED


if __name__ == "__main__":
    run(
        "../../data/doc_level_outlines",
        "../../data/summaries_doc_level_outlines"
    )
