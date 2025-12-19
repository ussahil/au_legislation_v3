from fastapi import FastAPI
from pydantic import BaseModel
from inference.pinecone_v2 import retriever

app = FastAPI(title="Au Legislation RAG API")

class Query(BaseModel):
    query:str 


@app.post("/chat")
async def chat_endpoint(payload:Query):
    result = retriever(payload.query)
    return {"answer":result}