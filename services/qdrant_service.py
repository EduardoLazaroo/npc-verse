from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct, VectorParams, Distance, PayloadSchemaType
)
import os
from uuid import uuid4
from dotenv import load_dotenv
from services.embedding_service import embed_text

load_dotenv()

qdrant = None
collection_name = "npc_memory"


def get_qdrant_client():
    global qdrant
    if qdrant is not None:
        return qdrant

    try:
        url = os.getenv("QDRANT_URL") or ""
        api_key = os.getenv("QDRANT_API_KEY") or ""
        url = url.strip('"').strip("'")
        api_key = api_key.strip('"').strip("'")

        qdrant = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=3
        )
        return qdrant
    except Exception as e:
        print(f"[QDRANT] Não foi possível conectar ao Qdrant: {e}")
        qdrant = None
        return None


def init_qdrant():
    q = get_qdrant_client()
    if q is None:
        print("[QDRANT] Ignorando inicialização: cliente indisponível")
        return False

    try:
        if not q.collection_exists(collection_name):
            q.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

        for field, schema in [("npc_id", PayloadSchemaType.INTEGER), ("type", PayloadSchemaType.KEYWORD)]:
            try:
                q.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=schema
                )
            except Exception:
                pass

        print(f"[QDRANT] Coleção '{collection_name}' pronta")
        return True
    except Exception as e:
        print(f"[QDRANT] Erro de inicialização: {e}")
        return False

def insert_npc_memory(npc_id, vector, text, memory_type="general", metadata=None):
    q = get_qdrant_client()
    if q is None:
        print("[QDRANT] Ignorando inserção de memória: cliente Qdrant indisponível")
        return None

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

    try:
        q.upsert(collection_name=collection_name, points=[point])
        return point.id
    except Exception as e:
        print(f"[QDRANT] Erro ao inserir memória: {e}")
        return None


def search_npc_memories(npc_id, query_text, memory_types=None, top_k=10, debug=False, min_score=0.3):
    query_vector = embed_text(query_text)

    if query_vector is None:
        return []

    q = get_qdrant_client()
    if q is None:
        return []

    must_conditions = [{"key": "npc_id", "match": {"value": npc_id}}]

    if memory_types:
        if isinstance(memory_types, str):
            memory_types = [memory_types]
        must_conditions.append({
            "key": "type",
            "match": {"any": memory_types}
        })

    try:
        results = q.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            query_filter={"must": must_conditions},
            with_payload=True,
            with_vectors=False
        )

        hits = getattr(results, "result", results) or []

        filtered = [hit for hit in hits if getattr(hit, "score", 0) >= min_score]

        if debug:
            print(f"\n[QDRANT DEBUG] {len(filtered)} memórias relevantes para: \"{query_text}\" (score >= {min_score})")
            for idx, hit in enumerate(filtered, 1):
                print(f"{idx}. Score: {hit.score:.4f}")
                print(f"   ID: {hit.id}")
                print(f"   Text: {hit.payload.get('text', 'sem texto')}")
                print(f"   Type: {hit.payload.get('type', 'sem tipo')}")
                print()

        return [{"text": hit.payload.get("text", ""), "score": hit.score} for hit in filtered]
    except Exception as e:
        print(f"[QDRANT] Erro ao buscar memórias: {e}")
        return []

