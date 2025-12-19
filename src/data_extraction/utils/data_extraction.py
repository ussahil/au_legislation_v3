import zipfile
from bs4 import BeautifulSoup
from pathlib import Path


# with zipfile.ZipFile(epub_path,"r") as epub:
#     # Get all the files
#     all_files = epub.namelist()
    
#     # Filter html files
#     html_files = [html for html in all_files if html.endswith(('.html',".xhtml",'.htm'))]
    
#     for html_file in html_files:
#         content = epub.read(html_file).decode("utf-8",errors="ignore")
#         soup = BeautifulSoup(content,"html.parser")

#         elements = []
#         for tag in soup.find_all(["h1","h2","h3","h4","h5","h6","p"]):
#             if tag.name.startswith('h'):
#                 level = int(tag.name[1])
#                 elements.append({
#                     "type":"Heading",
#                     "level":level,
#                     "text":tag.get_text(strip=True)

#                 })
#             elif tag.name == "p":
#                 text = tag.get_text(strip=True)
#                 if text:
#                     elements.append({
#                         "type":"paragraph",
#                         "text":text
#                     })
#         epub_contents[html_file] = elements
    

    # print(content[1000:2000])

# Path to EPUB file
def extractEPUB_to_html(epub_path: Path,output_val):
    # epub_path = '../../data/raw_data/C2025C00644.epub'
    epub_contents = {}
    output_dir = f"../../data/extracted_html/{output_val}"
    import os 
    with zipfile.ZipFile(epub_path, "r") as epub:
        all_files = epub.namelist()

        html_files = [f for f in all_files if f.lower().endswith(('.html', '.xhtml', '.htm'))]

        print("HTML files found:", html_files)

        for html_file in html_files:
            output_path = os.path.join(output_dir, html_file)

        # Ensure nested directories exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            file_data = epub.read(html_file)
            with open(output_path, "wb") as f:
                f.write(file_data)

            print("Saved:", output_path)