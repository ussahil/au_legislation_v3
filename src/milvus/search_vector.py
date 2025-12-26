from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
from milvus.utils.collection import create_milvus_collection
from milvus.utils.search_doc import search_doc_level_query,rerank_with_bge

# from utils.collection import create_milvus_collection
# from utils.search_doc import search_doc_level_query,rerank_with_bge


# client = MilvusClient(
#     uri="http://localhost:19530"
# )

# DOC_LEVEL =  "DOC_LEVEL"

# # user_query = "I did not get a pay raise what should I do?"
# user_query = "I just got a divorce , I am currently living with my child how much compensation am I entilled to under law"

# # Load in 8 bit model
# model = SentenceTransformer(
#     "Qwen/Qwen3-Embedding-0.6B",
#     model_kwargs={"load_in_8bit":True}
# )
# # Reranking 
# reranker = CrossEncoder(
#     "BAAI/bge-reranker-v2-m3",
#     device="cuda"  # or "cpu"
# )


# candidates = search_doc_level_query(
#     client=client,
#     user_query=user_query,
#     COLLECTION_LEVEL=DOC_LEVEL,
#     model=model
# )

# final_results = rerank_with_bge(
#     user_query=user_query,
#     candidates=candidates,
#     reranker=reranker,
#     top_k=5
# )


# client.load_collection(DOC_LEVEL)
# print(final_results)
