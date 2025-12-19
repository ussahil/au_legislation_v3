from utils.qwen3b_summary import summarize
from pathlib import Path
import json
import torch

SKIP_HEADS = {"short title", "commencement", "repeal"}

SYSTEM_PROMPT = """
Summarize statutory provisions.
Preserve legal terms and defined concepts.
Do not add interpretations or explanations.
Use neutral statutory language.
"""

def iter_json_files(root_folder):
    root = Path(root_folder)
    for act_dir in root.iterdir():
        if act_dir.is_dir():
            for json_file in act_dir.glob("*.json"):
                yield act_dir.name, json_file

def should_summarize(act_head):
    if not act_head:
        return True
    ah = act_head.lower()
    return not any(skip in ah for skip in SKIP_HEADS)

def save_output(doc_id, json_path, records, out_root):
    out_dir = Path(out_root) / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / json_path.name

    with open(out_file, "w") as f:
        json.dump(records, f, indent=2)

def process_file(json_path,doc_id,out_root,save_every=10):
    with open(json_path, "r") as f:
        records = json.load(f)

    for i, r in enumerate(records):
        act_head = r.get("ActHead")
        subsection_head = r.get("SubsectionHead")
        text = r.get("text", "").strip()

        # Administrative sections
        if not should_summarize(act_head):
            r["summary"] = {
                "level": "subsection",
                "category": "administrative",
                "act_head": act_head,
                "subsection_head": subsection_head,
                "text": "Administrative provision."
            }
            continue

        # Very short sections
        if len(text) < 120:
            r["summary"] = {
                "level": "subsection",
                "category": "substantive",
                "act_head": act_head,
                "subsection_head": subsection_head,
                "text": text
            }
            continue

        # Setting limit to ensure higher ones don't tap me out
        if len(text) > 6000:
            text = text[:6000]

        summary_text = summarize(
            text=text,
            act_head=act_head,
            subsection_head=subsection_head,
            system_prompt=SYSTEM_PROMPT
        )
        print(
        f"Summarizing record {i} | "
        f"chars={len(text)} | "
        f"act_head={act_head}")


        r["summary"] = {
            "level": "subsection",
            "category": "substantive",
            "act_head": act_head,
            "subsection_head": subsection_head,
            "text": summary_text
        }
        if i > 0 and i % save_every == 0:
            save_output(doc_id, json_path, records, out_root)
            print(f"  ✓ checkpoint saved at record {i}")

        if i % 20 == 0:
            torch.cuda.empty_cache()

    return records



def run(root_folder, out_root):
    for doc_id, json_path in iter_json_files(root_folder):
        print(f"Processing {json_path}")
        processed = process_file(json_path, doc_id, out_root)
        save_output(doc_id, json_path, processed, out_root)

run("../../data/final_json", "../../data/summaries_nsw_section_level")
