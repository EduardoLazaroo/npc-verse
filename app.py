from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import uuid

# Load .env
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# Qdrant setup
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
collection_name = "npc_memory"

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# DB connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", ""),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )


# Home: lista os NPCs no HTML
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs")
    npcs = cursor.fetchall()
    conn.close()
    return render_template("index.html", npcs=npcs)

# Rota para registrar NPC
@app.route('/register_npc', methods=['POST'])
def register_npc():
    data = request.json

    # 1. Salva no MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO npcs (name, role, location, personality, status) VALUES (%s, %s, %s, %s, %s)",
        (data['name'], data['role'], data['location'], data['personality'], data['status'])
    )
    conn.commit()
    npc_id = cursor.lastrowid
    conn.close()

    # 2. Salva personalidade inicial no Qdrant
    personality_text = data['personality']
    vector = model.encode(personality_text).tolist()
    memory_id = str(uuid.uuid4())

    qdrant.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=memory_id,
                vector=vector,
                payload={
                    "npc_id": npc_id,
                    "type": "personality",
                    "text": personality_text
                }
            )
        ]
    )

    return jsonify({"message": "NPC registrado com sucesso"}), 201

# Rota opcional para retornar NPCs em JSON (ex: para frontend React futuramente)
@app.route('/discover_npcs', methods=['GET'])
def discover_npcs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs")
    npcs = cursor.fetchall()
    conn.close()
    return jsonify(npcs)

# Iniciar o app
if __name__ == '__main__':
    app.run(debug=True)
