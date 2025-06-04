from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
import os

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "npc_memory"

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=384,  # tamanho do vetor do modelo MiniLM
        distance=Distance.COSINE
    )
)

print("✅ Collection 'npc_memory' criada com sucesso.")
