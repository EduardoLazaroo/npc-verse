from flask import Blueprint, request, jsonify
from models.npcverse_model import (
    save_npc, get_all_npcs, get_story_log
)
from services.interaction_service import process_interaction
from services.narrator_service import contextualize_interaction

npcverse_bp = Blueprint("npcverse", __name__)

@npcverse_bp.route("/register_npc", methods=["POST"])
def register_npc():
    data = request.get_json()
    save_npc(data)
    return jsonify({"message": "NPC registrado com sucesso!"})

@npcverse_bp.route("/story_log", methods=["GET"])
def story_log():
    return jsonify(get_story_log())

@npcverse_bp.route("/interact_npc", methods=["POST"])
def interact_npc():
    data = request.get_json()
    result = process_interaction(data)
    return jsonify(result)

@npcverse_bp.route("/narrate", methods=["POST"])
def narrate():
    data = request.get_json()
    response = contextualize_interaction(
        data["from"], data["to"], data["message"], data.get("memory")
    )
    return jsonify({"response": response})
