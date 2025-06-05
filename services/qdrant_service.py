from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct, Filter, FieldCondition, MatchValue,
    VectorParams, Distance, PayloadSchemaType
)
import os
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "npc_memory"

# Inicializa a coleção e o índice
def init_qdrant():
    if not qdrant.collection_exists(collection_name):
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    qdrant.create_payload_index(
        collection_name=collection_name,
        field_name="npc_id",
        field_schema=PayloadSchemaType.INTEGER
    )

init_qdrant()

def insert_npc_memory(npc_id, vector, text, memory_type="general"):
    point = PointStruct(
        id=str(uuid4()),  # IDs únicos por memória
        vector=vector,
        payload={
            "npc_id": npc_id,
            "type": memory_type,
            "text": text
        }
    )
    qdrant.upsert(collection_name=collection_name, points=[point])

def search_npc_memory(npc_id, query_vector):
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=1,
        query_filter=Filter(must=[FieldCondition(key="npc_id", match=MatchValue(value=npc_id))])
    )
    if results:
        hit = results[0]
        return {"text": hit.payload.get("text", ""), "score": hit.score}
    return None
