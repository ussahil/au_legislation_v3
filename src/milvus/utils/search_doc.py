# Level 1 Search 
def search_doc_level_query(client,user_query,COLLECTION_LEVEL,model):
    
    user_query_embeddings = model.encode(user_query,normalize_embeddings=True).astype("float32")

    results = client.search(
        collection_name=COLLECTION_LEVEL,
        data=[user_query_embeddings],
        anns_field="text_summary_embedding", 
        limit=5, #Get top 5 docs
        output_fields=['act','summary_text']
    )
    # Extract the actname that will be passed as filterable field
    retrieved_docs = []
    for hit in results[0]:
        retrieved_docs.append({
            "act":hit.entity.get("act"),
            "summary_text":hit.entity.get("summary_text"),
            "score": hit.distance
        })


    # retrieved_act_names = [hit["entity"]["act"] for hit in results[0]]
    return retrieved_docs