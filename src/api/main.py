from fastapi import FastAPI
from pydantic import BaseModel
# from inference.pinecone_v2 import retriever
from src.milvus.utils.search_doc import search_doc_level_query,rerank_with_bge, search_para_level_query
from src.milvus.constants import  PARA_LEVEL
from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv


client = MilvusClient(
    uri="http://localhost:19530"
)

DOC_LEVEL =  "DOC_LEVEL"

# Load in 8 bit model
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"load_in_8bit":True}
)
# Reranking 
reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3",
    device="cuda"  # or "cpu"
)
# client.load_collection(DOC_LEVEL)
# print(final_results)



app = FastAPI(title="Au Legislation RAG API")

class Query(BaseModel):
    query:str 


@app.post("/chat")
async def chat_endpoint(payload:Query):
    # result = search_doc_level_query(client,user_query=payload.query,COLLECTION_LEVEL=DOC_LEVEL,model=model)
    client.load_collection(DOC_LEVEL)
    candidates = search_doc_level_query(
    client=client,
    user_query=payload.query,
    COLLECTION_LEVEL=DOC_LEVEL,
    model=model)

    inital_results = rerank_with_bge(
        user_query=payload.query,
        candidates=candidates,
        reranker=reranker,
        top_k=5
    )
    id_for_act = [item['id_for_act'] for item in inital_results]
    acts_selected = [item['act'] for item in inital_results]

    client.load_collection(PARA_LEVEL)

    final_results =  search_para_level_query(client=client,
                            user_query=payload.query,
                            COLLECTION_LEVEL=PARA_LEVEL,
                            model=model,
                            reranker=reranker,
                            id_for_act=id_for_act,
                            jurisdiction="FRL",
                            country="AU")

    return {"acts_selected":acts_selected,"answer":final_results}
    


# async def low_level_endpoint(payload:Query)
   