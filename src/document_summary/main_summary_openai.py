from pathlib import Path
import json
from collections import OrderedDict


def iter_json_files(root_folder):
    root = Path(root_folder)
    for act_dir in root.iterdir():
        if act_dir.is_dir():
            for json_file in act_dir.glob("*.json"):
                yield act_dir.name, json_file


def extract_heads(json_path):
    with open(json_path, "r") as f:
        records = json.load(f)

    act_heads = OrderedDict()
    subsection_heads = OrderedDict()

    jurisdiction = None 
    act_name = None 

    for r in records:

        if jurisdiction is None :
            jurisdiction = r.get("jurisdiction")
        if act_name is None :
            act_name = r.get("act")

        act_head = r.get("ActHead")
        subsection_head = r.get("SubsectionHead")
        country = r.get("country")

        if act_head:
            act_heads[act_head.strip()] = None

        if subsection_head:
            subsection_heads[subsection_head.strip()] = None

    return (
        list(act_heads.keys()), 
        list(subsection_heads.keys()),
        jurisdiction,
        act_name,
        country)


def save_doc_outline(doc_id, act_heads, subsection_heads, jurisdiction,act_name,out_root,country):
    out_dir = Path(out_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"{doc_id}_outline.json"
    data = {
        "doc_id": doc_id,
        "jurisdiction": jurisdiction,
        "act": act_name,
        "country": country,
        "act_headings": act_heads,
        "subsection_headings": subsection_heads
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run(root_folder, out_root):
    for doc_id, json_path in iter_json_files(root_folder):
        print(f"Processing {json_path}")

        act_heads, subsection_heads,jurisdiction,act_name,country = extract_heads(json_path)
        save_doc_outline(doc_id, act_heads, subsection_heads,jurisdiction=jurisdiction,act_name=act_name,out_root=out_root,country=country)


run("../../data/final_json", "../../data/doc_level_outlines")