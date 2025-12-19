from lxml import etree
import json
from pathlib import Path

# -------------------------------
# PATH CONFIG (ONLY CHANGE)
# -------------------------------

RAW_XML_DIR = Path("../../data_nsw/raw_data")
OUTPUT_BASE_DIR = Path("../../data_nsw/initial_json")

OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# PROCESS EACH XML FILE
# -------------------------------

for XML_FILE in RAW_XML_DIR.glob("*.xml"):

    xml_name = XML_FILE.stem  # act-2005-028_2025-12-16
    output_dir = OUTPUT_BASE_DIR / xml_name
    output_dir.mkdir(parents=True, exist_ok=True)

    OUTPUT_CHUNKS = output_dir / "rag_chunks.json"

    # -------------------------------
    # ORIGINAL CODE (UNCHANGED)
    # -------------------------------

    tree = etree.parse(XML_FILE)
    root = tree.getroot()

    chunks = []
    definitions = []

    act_title = root.get("title")
    act_year = root.get("year")
    act_number = root.get("number")
    jurisdiction = "NSW"

    def extract_no(head):
        if head is None:
            return None
        no_elem = head.find("no")
        if no_elem is None:
            return None
        return " ".join("".join(no_elem.itertext()).split())

    def extract_heading(head):
        if head is None:
            return None
        heading_elem = head.find("heading")
        if heading_elem is None:
            return None
        text = "".join(heading_elem.itertext())
        return " ".join(text.split())

    def extract_level_info(elem, level_type):
        parent = elem.getparent()
        while parent is not None:
            if parent.tag == "level" and parent.get("type") == level_type:
                head = parent.find("head")
                return extract_no(head), extract_heading(head)
            parent = parent.getparent()
        return None, None

    def extract_text_recursive(elem):
        parts = []

        if elem.tag == "li":
            no_elem = elem.find("no")
            if no_elem is not None:
                no_text = "".join(no_elem.itertext()).strip()
                if no_text:
                    parts.append(no_text)

        for child in elem:
            if child.tag == "txt":
                text = " ".join(child.itertext()).strip()
                if text:
                    parts.append(text)
            elif child.tag not in {"no"}:
                parts.extend(extract_text_recursive(child))

        return parts

    def clean_text(elem):
        text = " ".join(extract_text_recursive(elem))
        return " ".join(text.split())

    def iter_subclauses(clause):
        for elem in clause.iter():
            if elem.tag == "tier" and elem.get("type") == "subclause":
                yield elem

    def extract_definitions(sub, section_no, subsection_no):
        for elem in sub.iter():
            if elem.tag == "defterm" and elem.get("type") == "definition":

                term = " ".join(elem.itertext()).replace("\n", " ").strip()

                txt_parent = elem.getparent()
                if txt_parent is None or txt_parent.tag != "txt":
                    continue

                full_txt = " ".join(txt_parent.itertext()).replace("\n", " ").strip()

                if full_txt.lower().startswith(term.lower()):
                    definition_text = full_txt[len(term):].strip()
                else:
                    definition_text = full_txt

                block = txt_parent.getparent()
                if block is not None:
                    for child in block:
                        if child.tag == "list":
                            definition_text += " " + clean_text(child)

                definitions.append({
                    "term": term,
                    "definition": definition_text.strip(),
                    "act": act_title,
                    "year": act_year,
                    "jurisdiction": jurisdiction,
                    "section": section_no,
                    "subsection": subsection_no
                })

    for clause in root.iter("level"):
        if clause.get("type") != "clause":
            continue

        head = clause.find("head")
        if head is None:
            continue

        section_no = extract_no(head)
        section_heading = extract_heading(head)

        part_no, part_heading = extract_level_info(clause, "part")
        division_no, division_heading = extract_level_info(clause, "division")
        subdivision_no, subdivision_heading = extract_level_info(clause, "subdivision")

        has_subclauses = False

        for sub in iter_subclauses(clause):
            has_subclauses = True

            sub_head = sub.find("head")
            sub_no = extract_no(sub_head)

            extract_definitions(sub, section_no, sub_no)

            text = clean_text(sub)
            if not text:
                continue

            chunks.append({
                "id": f"{act_number}_{section_no}{sub_no}",
                "text": text,
                "metadata": {
                    "act": act_title,
                    "year": act_year,
                    "jurisdiction": jurisdiction,
                    "part": part_no,
                    "part_heading": part_heading,
                    "division": division_no,
                    "division_heading": division_heading,
                    "subdivision": subdivision_no,
                    "subdivision_heading": subdivision_heading,
                    "section": section_no,
                    "subsection": sub_no,
                    "heading": section_heading
                }
            })

        if not has_subclauses:
            text = clean_text(clause)
            if text:
                chunks.append({
                    "id": f"{act_number}_{section_no}",
                    "text": text,
                    "metadata": {
                        "act": act_title,
                        "year": act_year,
                        "jurisdiction": jurisdiction,
                        "part": part_no,
                        "part_heading": part_heading,
                        "division": division_no,
                        "division_heading": division_heading,
                        "subdivision": subdivision_no,
                        "subdivision_heading": subdivision_heading,
                        "section": section_no,
                        "subsection": None,
                        "heading": section_heading
                    }
                })

    with open(OUTPUT_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ {xml_name}: Generated {len(chunks)} chunks")
