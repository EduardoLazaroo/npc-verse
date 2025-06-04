from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import pymysql
import uuid
import os

# Load .env
load_dotenv()

# Setup Qdrant
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
collection_name = "npc_memory"

# Verifica se a coleção existe e cria se não existir
if not qdrant.collection_exists(collection_name=collection_name):
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"✅ Coleção '{collection_name}' criada.")
else:
    print(f"⚠️ Coleção '{collection_name}' já existe.")

# Criação do índice no campo `npc_id`
qdrant.create_payload_index(
    collection_name=collection_name,
    field_name="npc_id",
    field_schema=PayloadSchemaType.INTEGER
)
print("🔧 Índice criado para 'npc_id'.")

# Setup modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Conexão com o banco MySQL
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", ""),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# Puxa NPCs do banco
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM npcs")
npcs = cursor.fetchall()
conn.close()

points = []

for npc in npcs:
    personality = npc['personality']
    vector = model.encode(personality).tolist()
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "npc_id": npc["id"],
            "type": "personality",
            "text": personality
        }
    )
    points.append(point)

# Inserir todos no Qdrant
if points:
    qdrant.upsert(
        collection_name=collection_name,
        points=points
    )
    print(f"✅ Inseridos {len(points)} vetores de personalidades no Qdrant.")
else:
    print("⚠️ Nenhum NPC encontrado para inserir.")
