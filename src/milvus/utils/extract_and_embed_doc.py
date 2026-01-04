import os 
from src.milvus.constants import BASE_DIR_PARA, PARA_LEVEL,get_embedding_model,get_milvus_client, MAX_CHARS, BATCH,VARCHAR_MAX_LENGTH, EMBED_BATCH
import json
import hashlib
model = get_embedding_model()
client = get_milvus_client()

def safe(x): return x or ""

def truncate_utf8(s: str, max_bytes: int) -> str:
    b = s.encode("utf-8")
    if len(b) <= max_bytes:
        return s
    return b[:max_bytes].decode("utf-8", errors="ignore")

def extract_and_embed_doc_low_level():
    """
    Docstring for extract_and_embed_doc_low_level

    Iterates over the json structructure to add in para level details
    """

    records = []
    embed_texts = []
    embed_payloads = []
    seen_hashes = set()
    try:
        iterator = client.query_iterator(
            collection_name=PARA_LEVEL,
            filter="content_hash != ''",
            output_fields=["content_hash"],
            batch_size=1000
        )
        while True:
            res = iterator.next()
            if not res:
                iterator.close()
                break
            seen_hashes.update(item["content_hash"] for item in res)
        
        print(f"Loaded {len(seen_hashes)} existing content hashes from Milvus")
    except Exception as e:
        print(f"Note: Could not load existing hashes (collection may be empty): {e}")
        seen_hashes = set()
    skipped_count = 0
    inserted_count = 0
    truncated_count = 0


    for act_folder in os.listdir(BASE_DIR_PARA):
        act_path = os.path.join(BASE_DIR_PARA,act_folder)
        if not os.path.isdir(act_path):
            continue
        for file in os.listdir(act_path):
            if not file.endswith(".json"):
                continue
            file_path = os.path.join(act_path,file)

            with open(file_path,'r') as f:
                docs = json.load(f)

            if not isinstance(docs, list):
                docs = [docs]

            for doc in docs:
                if not isinstance(doc, dict):
                    continue


                doc_id = doc.get("doc_id")
                id_for_act=doc.get("id") # This id it is responsible for the filtering to be done
                act = doc.get("act")
                ActHead = safe(doc.get("ActHead")) # if null trigger error
                SubsectionHead = safe(doc.get("SubsectionHead"))
                jurisdiction = doc.get("jurisdiction") # if null trigger error
                country = doc.get("country") # If null trigger error
                text = doc.get("text") or ""
             # I need to make it so that incase we have too much data then it splits into 2 but that would be for the advanced one
                normalized_text = " ".join(text.split())
                # Safe guard to Truncate max length 65535
                text_for_storage = truncate_utf8(normalized_text, VARCHAR_MAX_LENGTH)

                if len(normalized_text) > VARCHAR_MAX_LENGTH:
                    truncated_count += 1
                    print(f"Warning: Truncated text for {act} from {len(normalized_text)} to {VARCHAR_MAX_LENGTH} chars")
                text_reduced = normalized_text[:MAX_CHARS]
            

                content_hash = hashlib.md5(
                    f"{safe(id_for_act)}|{safe(ActHead)}|{safe(SubsectionHead)}|{normalized_text}".encode("utf-8")
                ).hexdigest()

                if content_hash in seen_hashes:
                    skipped_count +=1
                    continue

            # existing_hashes = set()
            

            # res = client.query(
            #     collection_name=PARA_LEVEL,
            #     filter=f'content_hash == "{content_hash}"',  # Changed from expr to filter
            #     output_fields=["content_hash"],
            #     limit=1
            # )
            # if res:
            #     print("Skipping this record ",act)
            #     continue

                seen_hashes.add(content_hash)

                # Unique ID is already being created by Milvus 

                embed_text = " ".join(x for x in [ActHead, SubsectionHead, text_reduced] if x
    )
                embed_texts.append(embed_text)
                embed_payloads.append({
                        "id_for_act": id_for_act,
                        "act": act,
                        "content_hash": content_hash,
                        "ActHead": ActHead,
                        "SubsectionHead": SubsectionHead,
                        "jurisdiction": jurisdiction,
                        "country": country,
                        "text": text_for_storage,
                    })

            

            # NOTE: IMPORTATANT stuff do NOT supply `id` on insert (auto_id enabled)

                # records.append({
                #     "id_for_act":id_for_act,
                #     "act":act,
                #     "content_hash":content_hash,
                #     "ActHead":ActHead,
                #     "SubsectionHead":SubsectionHead, 
                #     "jurisdiction":jurisdiction,
                #     "country":country,
                #     "text":text_for_storage,
                #     "text_embedding":embed_text_embedding

                # })
                if len(embed_texts) >= EMBED_BATCH:
                    embeddings = model.encode(
                        embed_texts,
                        batch_size=EMBED_BATCH,
                        normalize_embeddings=True,
                        show_progress_bar=False
                    )

                    for payload, emb in zip(embed_payloads, embeddings):
                        payload["text_embedding"] = emb.tolist()
                        records.append(payload)

                    embed_texts.clear()
                    embed_payloads.clear()

                if len(records) >= BATCH:
                
                    client.insert(PARA_LEVEL, records)
                    inserted_count += len(records)
                    print(f"Inserted batch: {len(records)} records (total: {inserted_count})")
                    records.clear()
    
    if embed_texts:
        embeddings = model.encode(
            embed_texts,
            batch_size=len(embed_texts),
            normalize_embeddings=True
    )
        for payload, emb in zip(embed_payloads, embeddings):
            payload["text_embedding"] = emb.tolist()
            records.append(payload)
        embed_texts.clear()
        embed_payloads.clear()

    if records:

        client.insert(PARA_LEVEL,records)
        inserted_count += len(records)
        print(f"Inserted final batch: {len(records)} records")

    client.flush(collection_name=PARA_LEVEL)
    print(f"Completed: {inserted_count} inserted,{truncated_count} truncated, {skipped_count} skipped")

