from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from utils.collection import create_milvus_collection
# from utils.search_doc import search_doc_level_query


client = MilvusClient(
    uri="http://localhost:19530"
)

DOC_LEVEL =  "DOC_LEVEL"


user_query = "Tell me about indexation inside Fair Work Act? "

# DOC_LEVEL = "document"
BASE_DIR = "../../data/summaries_doc_level_outlines"

create_milvus_collection(DOC_LEVEL,client)
    
   
# Load in 8 bit model
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"load_in_8bit":True}
)


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

            if not summary_text:
                print(f"{act} , {doc_id} , This is missing summary text data")
                continue

            pk = f"{jurisdiction}::{act}::{doc_id}"

            # existing = client.get(collection_name=DOC_LEVEL, ids=[pk])

            # print("PK:", pk, "EXISTS:", bool(existing))
            embedding = model.encode(summary_text, normalize_embeddings=True).tolist()

            # if client.get(collection_name=DOC_LEVEL, ids=[pk]):
            #     continue
            
            records.append({
                "id":pk,
                "text_summary_embedding": embedding,
                "act": act,
                "jurisdiction":jurisdiction,
                "country": country,
                "summary_text": summary_text,
            })
            # print(records)
    return records 

records = extract_embed_doc_level_summaries()
# print(records)
# print(len(records))
try:
    if records:
        client.insert(
            collection_name=DOC_LEVEL,
            data = records 
        )
        client.flush(collection_name=DOC_LEVEL)
except Exception as e:
    print("Insert Error probably same val error",e)

# client.insert(collection_name=DOC_LEVEL,) 

# Level 1 Search 

# print(search_doc_level_query(client,user_query,DOC_LEVEL,model))

