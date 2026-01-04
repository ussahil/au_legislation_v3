from bs4 import BeautifulSoup
import re
from pathlib import Path
import json 
import base64

def clean_text(t):
    """Normalize whitespace consistently."""
    return " ".join(t.split()).strip()


def extract_act_title(soup):
    if soup.title and soup.title.get_text(strip=True):
        return clean_text(soup.title.get_text())
    short_title_p = soup.find("p", class_="ShortT")
    if short_title_p:
        spans = short_title_p.find_all("span")
        if spans:
            title = "".join(span.get_text(strip=True) for span in spans)
            return clean_text(title)

    return None

def make_safe_id(prefix: str, act_name: str, output_val: str) -> str:
    raw = f"{prefix}::{act_name}::{output_val}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    return encoded

def parse_html(html,output_val):
    PARA_SUB_CLASSES = {"paragraphsub", "Definition", "notetext","notepara"}
    soup = BeautifulSoup(html, "html.parser")

    #Getting the actname for the specific document
    # act_name = clean_text(soup.title.get_text()) if soup.title else None
    act_name = extract_act_title(soup)

    results = []

    act_count = 0
    subsection_count = 0

    paragraph_count = 0
    paragraph_sub_count = 0

    current_act = None
    current_subsection = None

    # Regex patterns
    act_pattern = re.compile(r"ActHead", re.IGNORECASE)
    subsection_head_pattern = re.compile(r"SubsectionHead", re.IGNORECASE)
    toc_pattern = re.compile(r"^TOC", re.IGNORECASE)   # matches TOC1, TOC_2, TOC, etc.

    for tag in soup.find_all(['p', 'div', 'span']):

        classes = tag.get("class") or []

        #-............- IGNORE!! TOC that is the menu ----------
        if any(toc_pattern.match(c) for c in classes):
            continue

        if any(act_pattern.search(c) for c in classes):
            act_count += 1
            subsection_count = 0
            paragraph_count = 0
            paragraph_sub_count = 0

            current_act = clean_text(tag.get_text())
            continue

        if any(subsection_head_pattern.search(c) for c in classes):
            subsection_count += 1
            paragraph_count = 0
            paragraph_sub_count = 0

            current_subsection = clean_text(tag.get_text())
            continue

        if "subsection" in classes:
            # paragraph_count += 1
            paragraph_sub_count = 0

            text = clean_text(tag.get_text())
            if text:
                results.append({
                    "doc_id": output_val,
                    "id": make_safe_id("FRL", act_name, output_val),
                    "id_raw":f"{'FRL'}::{act_name}::{output_val}",
                    "ActHead": current_act,
                    "SubsectionHead": current_subsection,
                    "type": "subsection",
                    "text": text,
                    "jurisdiction": "FRL",
                    "act": act_name,
                    "country":"AU"
                })
            continue

        if PARA_SUB_CLASSES.intersection(classes):
            paragraph_sub_count += 1

            text = clean_text(tag.get_text())
            if text:
                results.append({
                    "doc_id":output_val,
                    "id": make_safe_id("FRL", act_name, output_val),
                    "id_raw":f"{'FRL'}::{act_name}::{output_val}",
                    "ActHead": current_act,
                    "SubsectionHead": current_subsection,
                    "type": "paragraphsub",
                    "text": text,
                    "jurisdiction": "FRL",
                    "act": act_name,
                    "country":"AU"
                })
            continue

        if "paragraph" in classes:
            paragraph_count += 1
            paragraph_sub_count = 0

            text = clean_text(tag.get_text())
            if text:
                results.append({
                    "doc_id":output_val,
                    "id": make_safe_id("FRL", act_name, output_val),
                    "id_raw":f"{'FRL'}::{act_name}::{output_val}",
                    "ActHead": current_act,
                    "SubsectionHead": current_subsection,
                    "type": "paragraph",
                    "text": text,
                    "jurisdiction": "FRL",
                    "act": act_name,
                    "country":"AU"
                })
            continue
        

    return results

def extractHTML_json(datapath:Path,output_val):

    with open(f"../../data/extracted_html/{output_val}/OEBPS/{datapath}/{datapath}.html",'r',encoding="utf-8") as f:
        html_content = f.read()

    data = parse_html(html_content,output_val)

    # Make sure folder exists
    output_folder = Path(f"../../data/initial_json/{output_val}")
    output_folder.mkdir(parents=True,exist_ok=True)

    output_json_path = f"{output_folder}/{datapath}.json"

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Saved JSON",output_json_path)

# extractHTML_json(Path('document_2'))