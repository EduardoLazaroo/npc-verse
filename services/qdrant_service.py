from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct, VectorParams, Distance, PayloadSchemaType
)
import os
from uuid import uuid4
from dotenv import load_dotenv
from services.embedding_service import embed_text

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "npc_memory"

def init_qdrant():
    if not qdrant.collection_exists(collection_name):
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    for field, schema in [("npc_id", PayloadSchemaType.INTEGER), ("type", PayloadSchemaType.KEYWORD)]:
        try:
            qdrant.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=schema
            )
        except Exception:
            pass

init_qdrant()

def insert_npc_memory(npc_id, vector, text, memory_type="general", metadata=None):
    payload = {
        "npc_id": npc_id,
        "type": memory_type,
        "text": text
    }
    if metadata:
        payload.update(metadata)

    point = PointStruct(
        id=str(uuid4()),
        vector=vector,
        payload=payload
    )
    qdrant.upsert(collection_name=collection_name, points=[point])
    return point.id

def search_npc_memories(npc_id, query_text, memory_types=None, top_k=10, debug=False):
    query_vector = embed_text(query_text)

    must_conditions = [{"key": "npc_id", "match": {"value": npc_id}}]

    if memory_types:
        if isinstance(memory_types, str):
            memory_types = [memory_types]
        must_conditions.append({
            "key": "type",
            "match": {"any": memory_types}
        })

    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        query_filter={
            "must": must_conditions
        },
        with_payload=True,
        with_vectors=False
    )

    if debug:
        print(f"\n[QDRANT DEBUG] Top {top_k} resultados para o texto: \"{query_text}\"")
        for idx, hit in enumerate(results, 1):
            print(f"{idx}. Score: {hit.score:.4f}")
            print(f"   ID: {hit.id}")
            print(f"   Text: {hit.payload.get('text', 'sem texto')}")
            print(f"   Type: {hit.payload.get('type', 'sem tipo')}")
            print()

    return [hit.payload["text"] for hit in results if "text" in hit.payload]
