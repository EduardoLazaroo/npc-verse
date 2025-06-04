from flask import Blueprint, request, jsonify
from services.db_service import register_npc_db, get_npc_by_name
from services.qdrant_service import insert_npc_memory, search_npc_memory
from services.embedding_service import embed_text

npc_bp = Blueprint('npc', __name__)

@npc_bp.route('/register_npc', methods=['POST'])
def register_npc():
    data = request.json
    npc_id = register_npc_db(data)
    vector = embed_text(data['personality'])
    insert_npc_memory(npc_id, vector, data['personality'])
    return jsonify({"message": "NPC registrado com sucesso"}), 201

@npc_bp.route('/discover_npcs', methods=['GET'])
def discover_npcs():
    from services.db_service import get_all_npcs
    return jsonify(get_all_npcs())

@npc_bp.route('/interact', methods=['POST'])
def interact():
    data = request.json
    npc = get_npc_by_name(data['to'])
    if not npc:
        return jsonify({"error": f"NPC '{data['to']}' não encontrado"}), 404

    query_vector = embed_text(data['message'])
    match = search_npc_memory(npc['id'], query_vector)

    if not match:
        return jsonify({
            "from": npc["name"],
            "to": data["from"],
            "emotion": "neutro",
            "response": "Não tenho informações suficientes para responder."
        })

    return jsonify({
        "from": npc["name"],
        "to": data["from"],
        "emotion": "neutro",
        "response": f"{npc['name']} lembra: \"{match['text']}\" (similaridade {match['score']:.2f})"
    })
