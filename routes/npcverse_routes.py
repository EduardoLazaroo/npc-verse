from flask import Blueprint, request, jsonify
from models.npcverse_model import (
    save_npc,
    get_npc_by_name,
    save_story_entry,
    update_npc_emotion,
    get_story_log_by_npc
)
import openai
import os
from dotenv import load_dotenv
from services.interaction_service import process_interaction, format_interaction_html

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

npcverse_bp = Blueprint('npcverse', __name__)

@npcverse_bp.route('/npc/<name>', methods=['GET'])
def get_npc_by_name_route(name):
    npc = get_npc_by_name(name)
    if not npc:
        return jsonify({"error": "NPC não encontrado."}), 404
    return jsonify(npc)


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

    interaction_data = {
        "from": sender,
        "to": receiver,
        "message": message
    }

    result = process_interaction(interaction_data)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    response_text = result.get("response")
    new_emotion = result.get("emotion", "neutro")
    new_mood = result.get("mood", "estável")
    html = result.get("html")

    print(f"Interação processada de {sender} para {receiver}")

    story_entry = f"{sender}: {message}\n{receiver}: {response_text}"
    save_story_entry(story_entry, npc_name=receiver)

    update_npc_emotion(npc['id'], new_emotion, new_mood)

    return jsonify({
        "from": receiver,
        "to": sender,
        "response": response_text,
        "emotion": new_emotion,
        "mood": new_mood,
        "html": html
    })

@npcverse_bp.route('/story_log', methods=['GET'])
def story_log_by_npc():
    npc_name = request.args.get('npc_name')
    if not npc_name:
        return jsonify({"error": "Parâmetro 'npc_name' é obrigatório."}), 400

    log = get_story_log_by_npc(npc_name)

    formatted_log = []

    for entry in log:
        try:
            user_line, npc_line = entry["entry"].split("\n", 1)

            sender, user_message = user_line.split(":", 1)
            receiver, npc_response = npc_line.split(":", 1)

            html = format_interaction_html(
                sender.strip(),
                receiver.strip(),
                user_message.strip(),
                npc_response.strip().strip('"')
            )

            formatted_log.append({
                "id": entry["id"],
                "created_at": entry["created_at"],
                "html": html
            })
        except Exception as e:
            print(f"Erro ao processar entrada {entry['id']}: {e}")
            continue

    return jsonify(formatted_log)

@npcverse_bp.route('/search_npc', methods=['POST'])
def search_npc():
    import json
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "Parâmetro 'query' é obrigatório."}), 400

    prompt = f"""
Você é um sistema de criação de NPCs para jogos e narrativas.
Baseado no termo genérico abaixo, gere apenas 1 personagem relevante.
Se ele existir você deve usa-lo, caso nâo, crie um novo personagem.
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
- avatar_url (strings)

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

        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        data = json.loads(content)

        if isinstance(data, list):
            data = data[0]

        nome = data.get("name", "npc")
        data["avatar_url"] = f"https://robohash.org/{nome}.png?set=set2"

    except Exception as e:
        return jsonify({"error": f"Erro ao gerar NPCs: {str(e)}"}), 500

    return jsonify(data)
