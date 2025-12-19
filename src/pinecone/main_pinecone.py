import json
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# --------------------------
# CONFIG
# --------------------------
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

root_data_dir = "../../data/final_json"
INDEX_NAME = "au-legislation-demo-v6"
EMBED_DIM = 1024
BATCH_SIZE = 100
MAX_CHARS = 20000

PROGRESS_FILE = "processed_ids.json"
COUNTER_FILE = "counter.json"       # <--- persistent counter

# --------------------------
# ACT TITLES
# --------------------------
ACT_TITLES = {
    "C2025C00644": "Fair Work Act 2009",
    "C2025C00341": "Family Law Act 1975",
    "C2025C00340REC01": "Evidence Act 1995",
    "C2025C00450": "Corporations Act 2001",
    "C2025C00653": "Crimes Act 1914",
    "C2025C00597": "Sex Discrimination Act 1984",
    "C2024C00243": "Work Health and Safety Act 2011",
    "F2025C01071": "Fair Work Regulations 2009",
    "F2025C00594REC01": "Federal Circuit and Family Court of Australia (Family Law) Rules 2021",
    "F2025C00826": "Federal Court Rules 2011"
}

# --------------------------
# LOAD MODEL (8-bit)
# --------------------------
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"load_in_8bit": True}
)

# --------------------------
# PINECONE INIT
# --------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# --------------------------
# LOAD PROGRESS
# --------------------------
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

print(f"Loaded {len(processed_ids)} previously processed items.")

# --------------------------
# LOAD PERSISTENT COUNTER
# --------------------------
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        unique_counter = json.load(f)
else:
    unique_counter = 0

print(f"Starting unique counter from: {unique_counter}")

# --------------------------
# LOAD ALL JSON
# --------------------------
def load_all_json(root_dir):
    items = []
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                file_path = os.path.join(folder_path, file)
                print("Loading:", file_path)

                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            items.extend(data)
                        else:
                            items.append(data)
                except Exception as e:
                    print("Error loading", file_path, e)

    return items

data_items = load_all_json(root_data_dir)
print(f"Total records found: {len(data_items)}")

# --------------------------
# chunking

def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

#
for batch in chunks(data_items, BATCH_SIZE):
    vectors = []

    for item in batch:
        item_id = item["id"]
        doc_id = item.get("doc_id", "")

        # Stable skip key
        static_key = f"{doc_id}_{item_id}"

        # Skip already processed items
        

        # Data extraction
        doc_title = ACT_TITLES.get(doc_id, "")
        act_head = item.get("ActHead") or ""
        sub_head = item.get("SubsectionHead") or ""
        text_body = item.get("text", "")[:MAX_CHARS]

        embed_text = (
            f"{doc_title}. Section: {act_head}. "
            f"Subsection: {sub_head}. Text: {text_body}"
        )

        emb = model.encode(embed_text).tolist()

        # ----- UNIQUE VECTOR ID (persistent counter) -----
        unique_counter += 1
        
        vector_id = f"{static_key}_{unique_counter}"
        if vector_id in processed_ids:
            continue


        vectors.append({
            "id": vector_id,
            "values": emb,
            "metadata": {
                "original_id": item_id,
                "doc_id": doc_id,
                "doc_title": doc_title,
                "ActHead": act_head,
                "SubsectionHead": sub_head,
                "type": item.get("type"),
                "text": text_body
            }
        })

        # Mark processed using static key
        processed_ids.add(vector_id)

    # --------------------------
    # BATCH UPLOAD
    # --------------------------
    if vectors:
        print(f"Uploading {len(vectors)} vectors...")
        index.upsert(vectors=vectors)

        # Save processed IDs
        with open(PROGRESS_FILE, "w") as f:
            json.dump(list(processed_ids), f)

        # Save persistent counter
        with open(COUNTER_FILE, "w") as f:
            json.dump(unique_counter, f)

        print(
            f"Progress saved. Processed: {len(processed_ids)}, "
            f"Counter: {unique_counter}"
        )

print("DONE! All items processed.Finally")
