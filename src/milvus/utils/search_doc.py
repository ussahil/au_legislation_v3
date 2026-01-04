from collections import defaultdict


def weighted_reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    weights: list[float],
    k: int = 60
) -> list[tuple[str, float]]:
    """
    ranked_lists: list of ranked doc_id lists
    weights: same length as ranked_lists
    k: RRF constant
    """
    assert len(ranked_lists) == len(weights)

    scores = defaultdict(float)

    for ranking, weight in zip(ranked_lists, weights):
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] += weight / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def rerank_with_bge(
    user_query: str,
    candidates: list[dict],
    reranker,
    top_k: int = 5
):
    pairs = [
        (user_query, c["summary_text"])
        for c in candidates
    ]

    scores = reranker.predict(pairs)

    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)

    return sorted(
        candidates,
        key=lambda x: x["rerank_score"],
        reverse=True
    )[:top_k]


# Level 1 Search 
def search_doc_level_query(client,
                           user_query:str,
                           COLLECTION_LEVEL:str,
                           model,
                           ann_k:int = 10,
                           rrf_k : int = 60,
                           rerank_k: int = 15,):
    
    user_query_embeddings = model.encode(user_query,
                                         normalize_embeddings=True
                                         ).astype("float32")

    summary_results = client.search(
        collection_name=COLLECTION_LEVEL,
        data=[user_query_embeddings],
        anns_field="text_summary_embedding", 
        limit=ann_k, #Get top 5 docs
        output_fields=['act','id_for_act',"summary_text"]
    )

    heading_results = client.search(
        collection_name = COLLECTION_LEVEL,
        data = [user_query_embeddings],
        anns_field="heading_embedding",
        limit = ann_k,
        output_fields = ['act','id_for_act','summary_text']
    )

    # Extract ranked Doc IDS
    summary_ranked_ids = [
        hit.entity.get("id_for_act") for hit in summary_results[0]
    ]

    heading_ranked_ids = [
        hit.entity.get("id_for_act") for hit in heading_results[0]
    ]

    # RRF -----
    fused = weighted_reciprocal_rank_fusion(
        ranked_lists=[summary_ranked_ids,heading_ranked_ids],
        weights=[1.2,0.8], #[1.0,1.5]
        k = rrf_k ,
    )

    # Doc Store
    doc_store = {}
    for hit in summary_results[0] + heading_results[0]:
        doc_store[hit.entity["id_for_act"]] = {
            "id_for_act": hit.entity["id_for_act"],
            "act": hit.entity["act"],
            "summary_text": hit.entity["summary_text"]
        }
    candidates = [
        doc_store[doc_id]
        for doc_id, _ in fused[:rerank_k]
        if doc_id in doc_store
    ]

    return candidates

def search_para_level_query(client,
                            user_query:str,
                            COLLECTION_LEVEL:str,
                            model,
                            reranker,
                            id_for_act:list[str],
                            jurisdiction:str,
                            country:str,
                            ann_k:int = 20,
                            rerank_k:int = 5):
    """
    Docstring for search_para_level_query

    Second level retriever Searches for specified docs identified by id_for_act
    """
    user_query_embeddings = model.encode(user_query,normalize_embeddings=True).astype("float32")

    filter_expr = f"id_for_act in {id_for_act}"

    summary_results = client.search(
        collection_name=COLLECTION_LEVEL,
        data = [user_query_embeddings],
        anns_field='text_embedding',
        limit=ann_k,
        filter = filter_expr,
        output_fields=['act',"ActHead","SubsectionHead","text"]
    )
    candidates = []
    for hit in summary_results[0]:
        candidates.append({
            "act": hit.entity.get("act"),
            "ActHead": hit.entity.get("ActHead"),
            "SubsectionHead": hit.entity.get("SubsectionHead"),
            "text": hit.entity.get("text"),
            "summary_text": hit.entity.get("text")
        })
    # Applying reranking now
    reranked_results = rerank_with_bge(
        user_query=user_query,
        candidates=candidates,
        reranker=reranker,
        top_k=rerank_k
    )
    return reranked_results


    # retrieved_act_names = [hit["entity"]["act"] for hit in results[0]]
    # return retrieved_docs