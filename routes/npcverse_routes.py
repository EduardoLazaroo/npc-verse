from flask import Blueprint, request, jsonify
from models.npcverse_model import (
    get_all_npcs,
    save_npc,
    get_npc_by_name,
    save_interaction,
    update_npc_emotion,
    get_npc_state,
    get_story_log,
    get_interactions_with_npc,
)
from services.interaction_service import process_interaction

npcverse_bp = Blueprint('npcverse', __name__)

@npcverse_bp.route('/register_npc', methods=['POST'])
def register_npc():
    data = request.json
    save_npc(data)
    return jsonify({"status": "NPC registrado com sucesso!"})

@npcverse_bp.route('/interact_npc', methods=['POST'])
def interact_npc():
    data = request.json
    sender = data.get("from", "Usuário")
    receiver = data.get("to")
    message = data.get("message")

    if not receiver or not message:
        return jsonify({"error": "Parâmetros inválidos."}), 400

    npc = get_npc_by_name(receiver)
    if not npc:
        return jsonify({"error": "NPC não encontrado."}), 404

    # Monta o dicionário que a função espera
    interaction_data = {
        "from": sender,
        "to": receiver,
        "message": message
    }

    # Chama a função process_interaction que retorna um dict com resposta e emoção
    result = process_interaction(interaction_data)

    # Se retornou erro, responde erro
    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    response_text = result.get("response")
    new_emotion = result.get("emotion", "neutro")
    new_mood = result.get("mood", "estável")  # Se quiser, pode ajustar na função para retornar mood também

    # Salva a interação (sender -> receiver, mensagem e resposta)
    save_interaction(sender, receiver, message, response_text)

    # Atualiza o estado emocional do NPC com os valores retornados
    update_npc_emotion(npc['id'], new_emotion, new_mood)

    return jsonify({
        "from": receiver,
        "to": sender,
        "response": response_text,
        "emotion": new_emotion,
        "mood": new_mood
    })

@npcverse_bp.route('/story_log', methods=['GET'])
def story_log():
    log = get_story_log()
    return jsonify(log)
