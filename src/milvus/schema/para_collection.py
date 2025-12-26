from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer

def create_milvus_collection_para(collection_LEVEL,client):
    if not client.has_collection(collection_name=collection_LEVEL):

        schema = MilvusClient.create_schema()

        # Add primary filed
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            auto_id = False,
            max_length=512
        )
        
        schema.add_field(
            field_name="act",
            datatype=DataType.VARCHAR,
            max_lenght=1000
        )
        schema.add_field(
            field_name="ActHead",
            datatype=DataType.VARCHAR,
            max_length=1000
        )
        schema.add_field(
            field_name="SubsectionHead",
            datatype=DataType.VARCHAR,
            max_length=2000
        )
        schema.add_field(
            field_name="jurisdiction",
            datatype=DataType.VARCHAR,
            max_length=100
        )
        schema.add_field(
            field_name="country",
            datatype=DataType.VARCHAR,
            max_length=100
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=20000
        )
