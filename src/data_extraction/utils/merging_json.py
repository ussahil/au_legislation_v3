import json

def merge_blocks(blocks):
    """Merge consecutive blocks that share ActHead , SubsectionHead"""

    if not blocks:
        return []
    
    merged = []
    current = blocks[0].copy()

    for item in blocks[1:]:
        same_section = (
            item['ActHead'] == current['ActHead'] and 
            item['SubsectionHead'] == current['SubsectionHead']
        )

        if same_section:
            current['text'] += " " + item['text']
        else:
            merged.append(current)
            current = item.copy()
    
    merged.append(current)
    return merged

# with open("../../data/initial_json/document_1.html.json") as w:
#     blocks =  json.load(w)

# merge_data = merge_blocks(blocks)
# with open("../../data/final_json/document_1_merged.json", "w", encoding="utf-8") as f:
#     json.dump(merge_data, f, indent=4, ensure_ascii=False)

#     print("Saved JSON")

# print(len(merge_data))