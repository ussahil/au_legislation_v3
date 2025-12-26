from pymilvus import MilvusClient , DataType
import json 
import os 
import re 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from src.milvus.schema.collection import create_milvus_collection
from src.milvus.schema.para_collection import create_milvus_collection_para
# from utils.search_doc import search_doc_level_query
from utils.helper_cleaner_summary import act_summary_cleaner




client = MilvusClient(
    uri="http://localhost:19530"
)

DOC_LEVEL =  "DOC_LEVEL"
PARA_LEVEL = "PARA_LEVEL"


user_query = "Tell me about indexation inside Fair Work Act? "

# DOC_LEVEL = "document"
BASE_DIR = "../../data/summaries_doc_level_outlines"

create_milvus_collection(DOC_LEVEL,client)
create_milvus_collection_para(collection_LEVEL=PARA_LEVEL,client=client)
    
   
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
            act_headings = doc.get("act_headings")
            cleaned_act_headings = act_summary_cleaner(act_headings)
            combined =  " ".join(cleaned_act_headings) # This is working now I need to work on cleaning staturtary obligations
            

            if not summary_text:
                print(f"{act} , {doc_id} , This is missing summary text data")
                continue

            pk = f"{jurisdiction}::{act}::{doc_id}"

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
                "id":pk,
                "act": act,                
                "summary_text": summary_text,
                "jurisdiction":jurisdiction,
                "country": country,
                "text_summary_embedding": summary_embedding,
                "heading_embedding": heading_embeddings
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
