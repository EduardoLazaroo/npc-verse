from flask import Blueprint, request, jsonify
from models.npcverse_model import (
    save_npc,
    get_npc_by_name,
    save_interaction,
    update_npc_emotion,
    get_story_log
)
import openai
import os
from dotenv import load_dotenv
from services.interaction_service import process_interaction

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

@npcverse_bp.route('/search_npc', methods=['POST'])
def search_npc():
    import json
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "Parâmetro 'query' é obrigatório."}), 400

    prompt = f"""
Você é um sistema de criação de NPCs para jogos e narrativas.
Baseado no termo genérico abaixo, gere apenas 1 personagem relevante e distinto.
Para esse personagem, responda em português e apenas em formato JSON com os seguintes campos:

- name (string)
- origin_world (string)
- archetype (string)
- alignment (string)
- personality_traits (string)
- voice_style (string)
- mood (string)
- emotion (string)
- skills (string)
- known_for (string)
- catchphrase (string)
- backstory (string)
- tags (lista de strings)
- avatar_url (string, pode ser placeholder)

Termo de busca: "{query}"

Por favor, retorne apenas o JSON, nada mais.
"""

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        content = completion.choices[0].message.content.strip()

        # Remove ```json e ``` do começo e fim, se existirem
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        # Carrega o JSON (pode ser lista ou objeto)
        data = json.loads(content)

        # Se for lista, pega só o primeiro item
        if isinstance(data, list):
            data = data[0]

    except Exception as e:
        return jsonify({"error": f"Erro ao gerar NPCs: {str(e)}"}), 500

    return jsonify(data)
