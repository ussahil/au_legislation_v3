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
    for act_dir in root.iterdir():
        if act_dir.is_dir():
            for json_file in act_dir.glob("*.json"):
                yield act_dir.name, json_file



def save_output(doc_id, json_path, record, out_root):
    out_dir = Path(out_root) / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / json_path.name

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

# -----------------------------
# Core processing (ONE Act)
# -----------------------------

def process_file(json_path, doc_id, out_root):
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        record = records[0]

    jurisdiction = record.get("jurisdiction")
    act = record.get("act")
    act_headings = record.get("act_headings", [])
    country = record.get("country")
    subsection_headings = record.get("subsection_headings", [])

    print(f"Summarizing Act: {act}")

    summary_text = summarize(
        jurisdiction=jurisdiction,
        act=act,
        act_headings=act_headings,
        # subsection_headings=subsection_headings,
        system_prompt=SYSTEM_PROMPT
    )

    record["act_retrieval_summary"] = summary_text

    save_output(doc_id, json_path, record, out_root)

    torch.cuda.empty_cache()

    return record


def run(root_folder, out_root):
    for doc_id, json_path in iter_json_files(root_folder):
        print(f"Processing {json_path}")
        process_file(json_path, doc_id, out_root)



if __name__ == "__main__":
    run(
        "../../data/doc_level_outlines", # "../../data/final.json"
        "../../data/summaries_doc_level_outlines"
    )