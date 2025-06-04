from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue

load_dotenv()

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

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs")
    npcs = cursor.fetchall()
    conn.close()
    return render_template("index.html", npcs=npcs)

@app.route('/register_npc', methods=['POST'])
def register_npc():
    data = request.json

    # Salva NPC no MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO npcs (name, role, location, personality, status) VALUES (%s, %s, %s, %s, %s)",
        (data['name'], data['role'], data['location'], data['personality'], data['status'])
    )
    conn.commit()
    npc_id = cursor.lastrowid
    conn.close()

    # Salva vetor de personalidade no Qdrant, usando npc_id numérico como ID do ponto para manter relação
    personality_text = data['personality']
    vector = model.encode(personality_text).tolist()

    point = PointStruct(
        id=npc_id,  # usar npc_id numérico para manter consistência
        vector=vector,
        payload={
            "npc_id": npc_id,
            "type": "personality",
            "text": personality_text
        }
    )
    qdrant.upsert(
        collection_name=collection_name,
        points=[point]
    )

    return jsonify({"message": "NPC registrado com sucesso"}), 201

@app.route('/discover_npcs', methods=['GET'])
def discover_npcs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs")
    npcs = cursor.fetchall()
    conn.close()
    return jsonify(npcs)

@app.route('/interact', methods=['POST'])
def interact():
    data = request.json
    npc_name = data.get("to")
    message = data.get("message")
    from_agent = data.get("from")

    if not npc_name or not message:
        return jsonify({"error": "Campos 'to' e 'message' são obrigatórios"}), 400

    # Busca NPC no banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs WHERE name = %s", (npc_name,))
    npc = cursor.fetchone()
    conn.close()

    if not npc:
        return jsonify({"error": f"NPC '{npc_name}' não encontrado"}), 404

    # Codifica mensagem para vetor
    query_vector = model.encode(message).tolist()

    # Busca vetor mais parecido no Qdrant filtrando pelo npc_id
    search_result = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=1,
        query_filter=Filter(
            must=[
                FieldCondition(key="npc_id", match=MatchValue(value=npc['id']))
            ]
        )
    )

    if not search_result:
        return jsonify({
            "from": npc_name,
            "to": from_agent,
            "emotion": "neutro",
            "response": "Não tenho informações suficientes para responder."
        })

    top_match = search_result[0]
    response_text = f"{npc_name} lembra: \"{top_match.payload.get('text', '')}\" (similaridade {top_match.score:.2f})"

    return jsonify({
        "from": npc_name,
        "to": from_agent,
        "emotion": "neutro",
        "response": response_text
    })

if __name__ == '__main__':
    app.run(debug=True)
