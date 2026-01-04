from pymilvus import MilvusClient , DataType
import json 
import os 
from sentence_transformers import SentenceTransformer

def create_milvus_collection_para(collection_LEVEL,client):
    if  client.has_collection(collection_name=collection_LEVEL):
        return
    else: 

        schema = MilvusClient.create_schema()

        # Add primary filed
        schema.add_field(
            field_name="id",
            datatype=DataType.INT64,
            is_primary=True,
            auto_id = True,
            # max_length=512
        )
        # for deduplication
        schema.add_field(
            field_name="content_hash",
            datatype=DataType.VARCHAR,
            max_length=100
        )

        schema.add_field(
            field_name="id_for_act",
            datatype=DataType.VARCHAR,
            max_length=512
        )
        schema.add_field(
            field_name="act",
            datatype=DataType.VARCHAR,
            max_length=1000
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
            max_length=64
        )
        schema.add_field(
            field_name="country",
            datatype=DataType.VARCHAR,
            max_length=100
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=65535
        )
        schema.add_field(
            field_name="text_embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim= 1024
        )

        # Prepare Index_ parameters
        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="text_embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="id_for_act",
            index_type="INVERTED"
        )
        index_params.add_index(
            field_name="content_hash",
            index_type="INVERTED"
        )

        client.create_collection(
            collection_name=collection_LEVEL,
            schema=schema,
            index_params=index_params
        )
