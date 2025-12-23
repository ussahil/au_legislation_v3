from pathlib import Path
import os 
import json

from utils.data_extraction import extractEPUB_to_html
from utils.soup_extraction import extractHTML_json
from utils.merging_json import merge_blocks

def process_all_html(root_folder,output_val):
    for dir_name in os.listdir(root_folder):
        dir_path = os.path.join(root_folder,dir_name)

        if not os.path.isdir(dir_path):
            continue

        for file in os.listdir(dir_path):
            if file.lower().endswith(".html"):
                print(f"Processing: {dir_name}")

                extractHTML_json(Path(dir_name),output_val)
                break



def process_final_json(root_folder,output_val): 
    """
     Pass in root folder and for every json file it will run merge block which will preprocess and paste cleaned file in final_json.
    """
    for file in os.listdir(root_folder):
        # merge_blocks(file)
        with open(f"{root_folder}/{file}") as w:
            blocks = json.load(w)
            # print(blocks)
            if blocks == [] or len(blocks) == 0 :
                continue # Will this skip
        
        merge_data = merge_blocks(blocks)

        output_path = f"../../data/final_json/{output_val}"

        os.makedirs(output_path, exist_ok=True)

        output_file_path = f"{output_path}/{file}"

        with open(f"{output_file_path}","w",encoding="utf-8") as f:
            json.dump(merge_data,f,indent=4,ensure_ascii=False)

            print("Final final has been created",file)

all_epub_files = os.listdir("../../data/raw_data") 
for epub in all_epub_files:
    exact_file_path = f"../../data/raw_data/{epub}"
    extractEPUB_to_html(Path(exact_file_path),epub[:-5])
    process_all_html(f'../../data/extracted_html/{epub[:-5]}/OEBPS',epub[:-5])
    process_final_json(f"../../data/initial_json/{epub[:-5]}",epub[:-5])


    print(epub)
# extractEPUB_to_html(Path("../../data/raw_data/F2025C00826.epub")) #data/raw_data/F2025C00826.epub

# process_all_html('../../data/extracted_html/OEBPS')

# process_final_json("../../data/initial_json")