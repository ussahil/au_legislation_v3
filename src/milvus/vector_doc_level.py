from pymilvus import MilvusClient , DataType
import json 
import os 
import re 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from src.milvus.schema.collection import create_milvus_collection
from src.milvus.schema.para_collection import create_milvus_collection_para
# from utils.search_doc import search_doc_level_query
# from utils.helper_cleaner_summary import act_summary_cleaner

from src.milvus.constants import get_milvus_client,get_embedding_model , PARA_LEVEL , DOC_LEVEL, BATCH
from src.milvus.utils.extract_and_embed_summaries import extract_embed_doc_level_summaries
from src.milvus.utils.extract_and_embed_doc import extract_and_embed_doc_low_level

client = get_milvus_client()
# Load in 8 bit model
model = get_embedding_model()


user_query = "Tell me about indexation inside Fair Work Act? "

# DOC_LEVEL = "document"

create_milvus_collection(DOC_LEVEL,client) 
create_milvus_collection_para(PARA_LEVEL,client)
# create_milvus_collection_para(collection_LEVEL=PARA_LEVEL,client=client)
      
extract_embed_doc_level_summaries()
print("-------------------- Embededding of summaries has been completed ---------")
extract_and_embed_doc_low_level()
# print(records)
# print(len(records))