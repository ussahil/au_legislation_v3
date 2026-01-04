import os 
from src.milvus.constants import BASE_DIR , DOC_LEVEL , PARA_LEVEL , get_embedding_model , get_milvus_client, BATCH
import json 
from src.milvus.utils.helper_cleaner_summary import act_summary_cleaner

model = get_embedding_model()
client = get_milvus_client()

def extract_embed_doc_level_summaries():
    """
    Logic to iterate over the json structure and get the required_data
    """
    
    records = []

    for act_folder in os.listdir(BASE_DIR):
        act_path = os.path.join(BASE_DIR,act_folder)
        if not os.path.isdir(act_path):
            continue
        for file in os.listdir(act_path):
            if not file.endswith(".json"):
                continue
            file_path = os.path.join(act_path,file)

            with open(file_path,"r") as f:
                doc = json.load(f)

            jurisdiction = doc.get("jurisdiction")
            act = doc.get("act")
            doc_id = doc.get("doc_id")
            summary_text = doc.get("act_retrieval_summary")
            country = doc.get("country")
            act_headings = doc.get("act_headings")
            cleaned_act_headings = act_summary_cleaner(act_headings)
            combined =  " ".join(cleaned_act_headings) # This is working now I need to work on cleaning staturtary obligations
            

            if not summary_text:
                print(f"{act} , {doc_id} , This is missing summary text data")
                continue

            # pk = f"{jurisdiction}::{act}::{doc_id}"
            pk = doc.get("id")

            # existing = client.get(collection_name=DOC_LEVEL, ids=[pk])
            if client.get(collection_name=DOC_LEVEL, ids=[pk]):
                continue
            

            # print("PK:", pk, "EXISTS:", bool(existing))
            summary_embedding = model.encode(summary_text, normalize_embeddings=True).tolist()

            if combined.strip():
                # Heading embeddinsg 
                heading_embeddings = model.encode(
                    combined,
                    normalize_embeddings=True
                ).tolist()
            else:
                # Fallback
                heading_embeddings = summary_embedding

            
            
            records.append({
                "id_for_act":pk,
                "act": act,                
                "summary_text": summary_text,
                "jurisdiction":jurisdiction,
                "country": country,
                "text_summary_embedding": summary_embedding,
                "heading_embedding": heading_embeddings
            })

            if len(records) >= BATCH:
                client.insert(DOC_LEVEL,records)
                records.clear()
            # print(records)
    if records:
        client.insert(DOC_LEVEL,records)
    client.flush(collection_name=DOC_LEVEL)