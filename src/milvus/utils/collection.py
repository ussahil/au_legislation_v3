from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv



def create_milvus_collection(collection_LEVEL,client):
    if not client.has_collection(collection_name=collection_LEVEL):

        schema = MilvusClient.create_schema()

        # Add primary field
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            auto_id = False,
            max_length=512 
        )
        # Add in metaData Fields
        schema.add_field(
            field_name="act",
            datatype=DataType.VARCHAR,
            max_length=3000
        )

        schema.add_field(
            field_name="summary_text",
            datatype=DataType.VARCHAR,
            max_length=10000
        )

        schema.add_field(
            field_name="jurisdiction",
            datatype=DataType.VARCHAR,
            max_length=64
        )
        schema.add_field(
            field_name="country",
            datatype=DataType.VARCHAR,
            max_length=100,
        )

        schema.add_field(
            field_name="text_summary_embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=1024  # 
        )
        schema.add_field(
            field_name="heading_embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=1024
        )

        # Prepare Index Paramaters
        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="text_summary_embedding", 
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="heading_embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )

        client.create_collection(
            collection_name=collection_LEVEL,
            schema=schema,
            index_params=index_params
        )