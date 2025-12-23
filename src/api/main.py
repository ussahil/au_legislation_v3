from fastapi import FastAPI
from pydantic import BaseModel
# from inference.pinecone_v2 import retriever
from milvus.search_vector import search_doc_level_query
from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
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
app = FastAPI(title="Au Legislation RAG API")

class Query(BaseModel):
    query:str 


@app.post("/chat")
async def chat_endpoint(payload:Query):
    result = search_doc_level_query(client,user_query=payload.query,COLLECTION_LEVEL=DOC_LEVEL,model=model)
    return {"answer":result}