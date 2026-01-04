from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from pathlib import Path

CLIENT_URI="http://localhost:19530"
DOC_LEVEL =  "DOC_LEVEL"
PARA_LEVEL = "PARA_LEVEL"
VARCHAR_MAX_LENGTH = 60000 #65535

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
BASE_DIR = DATA_DIR / "summaries_doc_level_outlines"
BASE_DIR_PARA = DATA_DIR / "final_json"
# BASE_DIR = "../../data/summaries_doc_level_outlines" #inacRagAi/data/summaries_doc_level_outlines
# BASE_DIR_PARA = "../../data/final_json"
BATCH = 64
EMBED_BATCH = 8
MAX_CHARS = 20000
_model = None 
_client = None 
# Based on singleton pattern load once use everyhere else

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
        "Qwen/Qwen3-Embedding-0.6B",
        model_kwargs={"load_in_8bit":True}
    )
    return _model

def get_milvus_client():
    global _client
    if _client is None:
        _client = MilvusClient(
            uri=CLIENT_URI
        )
    return _client
