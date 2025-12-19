import os 
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
INDEX_NAME = "au-legislation-demo-v5"

# Initialize once
pc = Pinecone(api_key=PINECONE_API_KEY)
dense_index = pc.Index(INDEX_NAME)
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# Setup reranking max token
MAX_RERANK_TOKENS = 900

def truncate_for_rerank(text, max_tokens=MAX_RERANK_TOKENS):
    return text[: max_tokens * 4]

def retriever(query:str):
    
    # query = "My trello is not working "
    # query = "How do sentencing guidelines apply to repeat offenders? "
    is_legal = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": """Classify whether the user's query is related to law, legislation, "
                "legal concepts, crime, justice, courts, rights, penalties, "
                "government rules, or anything requiring legal explanation. "
                "Be INCLUSIVE. If the query even slightly touches law, crime, "
                "regulation, or legal systems, respond ONLY: yes. Only for completely unreleated query respond no "
                "Respond ONLY: yes or no."""},
            {"role": "user", "content": query}
        ]
    ).choices[0].message.content.strip().lower()

    if is_legal != "yes":
        print(is_legal)
        return "This question does not appear to relate to Australian legislation. Please rephrase if you need legal interpretation."


    

    query_emb = model.encode(query).tolist()

    # Search the dense index
    results = dense_index.query(
        namespace="",
        top_k=10,
        vector=query_emb,
        include_metadata=True
    )

   

    documents = [
        {
            "id": m.id,
            "text": truncate_for_rerank(m.metadata.get("text", ""))
        }
        for m in results.matches
    ]

    # Rerank the results to get top 5
    reranked_results = pc.inference.rerank(
        model="bge-reranker-v2-m3",
        query=query,
        documents=documents,
        top_n=5,
        return_documents=True
    )

    # Fetch full documents
    top_ids = [r.document["id"] for r in reranked_results.data]
    full_docs = dense_index.fetch(ids=top_ids, namespace="")

    # print("\n===== FINAL FULL RESULTS =====")
    # for doc_id, record in full_docs['vectors'].items():
    #     print("\nID:", doc_id)
    #     print("Act:", record.get('metadata', {}).get("doc_title"))
    #     print("ActHead",record.get('metadata',{}).get("ActHead"))
    #     print("SubsectionHead",record.get('metadata',{}).get("SubsectionHead"))
    #     print("Section:", record.get('metadata', {}).get("original_id"))
    #     print("Full Text:", record.get('metadata', {}).get("text", "")) #[:500], "..."
    scores = {}

    for r in reranked_results.data:
        doc_id = r.document["id"]
        score = r.score
        scores[doc_id] = score
        context_chunks = []

    for doc_id, record in full_docs['vectors'].items():
        act = record.get("metadata", {}).get("doc_title")
        original_id = record.get("metadata", {}).get("id")
        acthead = record.get('metadata',{}).get("ActHead")
        subsectionhead = record.get('metadata',{}).get("SubsectionHead")
        text = record.get("metadata", {}).get("text", "")

        context_chunks.append(f"Original Document: {act}\n id:{original_id}\n Section: {acthead}\n SubsectionHead:{subsectionhead}\n Content: {text}")

    context_text = "\n\n---\n\n".join(context_chunks)


    prompt = f"""
You are an expert assistant for Australian Legislation.

You are given multiple retrieved chunks from legislation.
Each chunk includes a relevance score (higher = more relevant).

Your instructions:
- FIRST identify the single chunk with the highest relevance score.
- Base your answer primarily on that chunk.
- You may use other chunks ONLY if they directly clarify or reinforce the meaning of the highest-scoring chunk.
- DO NOT mix unrelated chunks. Ignore any chunk that does not help answer the question.
- DO NOT speculate. Only use what is written.

Your task:
- Use the retrieved sections to answer the question as accurately as possible.
- If the text does not directly mention the user’s topic, you may still provide a partial answer using relevant legislative concepts contained in the retrieved text.
- You are allowed to interpret and explain how the retrieved provisions *could* apply, as long as you stay grounded in the retrieved text.

Rules:
- DO NOT invent legal provisions not present in the text.
- DO NOT claim the law says something exact when the wording is not present.
- You MAY explain mechanisms (e.g., cumulative sentencing, timing rules) that are explicitly described.
- If absolutely no part of the retrieved text is relevant, say:
  “Although the retrieved sections don’t explicitly address this topic, here is the relevant information that can be drawn from them:”
  …and give a grounded explanation.

User Query:
{query}
Scores:
{scores}
Retrieved Legislative Sections (with relevance scores):
{context_text}

Final Answer (only using and interpreting the above text):
"""

    return prompt
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are an expert assistant for Australian Legislation."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.2
    # )
    # print("\n===== FINAL GPT ANSWER =====\n")
    # print(response.choices[0].message.content)

    # print("--------------Context_text----------")
    # print(context_text)
    # print("\n===== RERANKED RESULTS WITH SCORES =====")
    # for r in reranked_results.data:
    #     print(f"ID: {r.document['id']}  |  Score: {r.score:.4f}")


    # return response.choices[0].message.content

   
print(retriever("What types of employers are specified as State public sector employers according to Regulation 1.15A"))