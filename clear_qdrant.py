from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import os
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "npc_memory"

# ⚠️ Apaga tudo e recria a coleção
qdrant.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

print(f"✅ Coleção '{collection_name}' limpa e recriada com sucesso.")
