from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from milvus.utils.collection import create_milvus_collection
from milvus.utils.search_doc import search_doc_level_query


# client = MilvusClient(
#     uri="http://localhost:19530"
# )

# DOC_LEVEL =  "DOC_LEVEL"

# user_query = "I did not get a pay raise what should I do?"

# Load in 8 bit model
# model = SentenceTransformer(
#     "Qwen/Qwen3-Embedding-0.6B",
#     model_kwargs={"load_in_8bit":True}
# )

# client.load_collection(DOC_LEVEL)
# print(search_doc_level_query(client,user_query,DOC_LEVEL,model))
