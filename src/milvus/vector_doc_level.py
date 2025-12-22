from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


client = MilvusClient(
    uri="http://localhost:19530"
)

user_query = ""

DOC_LEVEL = "document"
BASE_DIR = "../../data/summaries_doc_level_outlines"


# if not client.has_collection(collection_name=DOC_LEVEL):

#     schema = MilvusClient.create_schema()

#     # Add primary field
#     schema.add_field(
#         field_name="id",
#         datatype=DataType.VARCHAR,
#         is_primary=True,
#         auto_id = True 
#     )
#     # Add in metaData Fields
#     schema.add_field(
#         field_name="act",
#         datatype=DataType.VARCHAR
#     )

#     schema.add_field(
#         field_name="summary",
#         datatype=DataType.VARCHAR,
#     )

#     schema.add_field(
#         field_name="jurisdiction",
#         datatype=DataType.VARCHAR
#     )
#     schema.add_field(
#         field_name="country",
#         datatype=DataType.VARCHAR,
#         max_length=100
#     )

#     schema.add_field(
#         field_name="text_summary_embedding",
#         datatype=DataType.FLOAT_VECTOR,
#         dim=1024  # 
#     )

#     # Prepare Index Paramaters
#     index_params = client.prepare_index_params()

#     index_params.add_index(
#         field_name="id",
#         index_type="AUTOINDEX"
#     )

#     index_params.add_index(
#         field_name="text_summary_embedding", 
#         index_type="AUTOINDEX",
#         metric_type="COSINE"
#     )

#     client.create_collection(
#         collection_name=DOC_LEVEL,
#         schema=schema,
#         index_params=index_params
#     )
   
# Load in 8 bit model
# model = SentenceTransformer(
#     "Qwen/Qwen3-Embedding-0.6B",
#     model_kwargs={"load_in_8bit":True}
# )

# embedding_fn = model.encode("").tolist() # Edit Later to get Qwen to encode it


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
            summary_text = doc.get("act_retrieval_summary",{}).get("text")

            print({
                "embedding": "",
                "jurisdiction": jurisdiction,
                "act": act,
                "doc_id": doc_id,
                "summary_text": summary_text,
            })




# client.insert(collection_name=DOC_LEVEL,) 

# Level 1 Search 
# user_query_embeddings = model.encode(user_query)

# results = client.search(
#     collection_name=DOC_LEVEL,
#     data=[user_query_embeddings],
#     anns_field="text_summary_embedding", 
#     limit=5, #Get top 5 docs
#     output_fields=['act','country','jurisdiction']
# )
# # Extract the actname that will be passed as filterable field
# retrieved_act_names = [hit["entity"]["act_name"] for hit in results[0]]

extract_embed_doc_level_summaries()