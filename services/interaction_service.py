from models.npcverse_model import (
    save_story_entry,
    get_npc_by_name,
    save_interaction,
    update_npc_emotion,
    get_npc_state,
    get_interactions_with_npc
)
from services.qdrant_service import insert_npc_memory, search_npc_memories
from services.embedding_service import embed_text
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def detect_emotion_from_message(message):
    prompt = f"""
Classifique o sentimento principal desta mensagem como uma das emoções a seguir: grato, raiva, triste, feliz, neutro, agressivo, sarcástico, confuso, calmo, ansioso, frustrado.
Mensagem: "{message}"
Responda apenas com o nome da emoção mais apropriada.
"""
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10,
        )
        emotion = completion.choices[0].message.content.strip().lower()
        return emotion
    except Exception:
        return "neutro"


def format_interaction_html(sender, receiver, user_message, npc_response):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return f'''
    <div class="chat-message">
        <div class="chat-row user-message">
            <div class="bubble user">
                <strong>{sender}:</strong><br>{user_message}
            </div>
            <div class="timestamp">{timestamp}</div>
        </div>
        <div class="chat-row npc-message">
            <div class="bubble npc">
                <strong>{receiver}:</strong><br>{npc_response}
            </div>
            <div class="timestamp">{timestamp}</div>
        </div>
    </div>
    '''

def process_interaction(data):
    sender = data['from']
    receiver = data['to']
    message = data['message']

    npc = get_npc_by_name(receiver)
    if not npc:
        return {"error": f"NPC '{receiver}' não encontrado"}

    npc_state = get_npc_state(npc['id'])
    current_emotion = npc_state.get("emotion", "neutro")
    current_mood = npc_state.get("mood", "estável")

    sql_history = get_interactions_with_npc(receiver)[-10:]
    formatted_sql_history = [
        f"{entry['sender']} disse: \"{entry['message']}\"\n{entry['receiver']} respondeu: \"{entry['response']}\""
        for entry in sql_history
    ]

    vector_memories = search_npc_memories(
        npc_id=npc['id'],
        query_text=message,
        memory_types=["mensagem_usuario", "resposta_npc"],
        top_k=3
    )
    formatted_vector_memories = [f"(memória relevante) {mem}" for mem in vector_memories]

    full_context = "\n".join(formatted_vector_memories + formatted_sql_history)

    personality = npc.get("personality", "")

    prompt = f"""
Você é {npc['name']}, um NPC com a seguinte personalidade: {personality}.
Seu estado emocional atual é {current_emotion} e seu humor está {current_mood}.

Contexto recuperado da memória:
{full_context}

Agora {sender} diz: "{message}"

Responda apenas o texto da fala do NPC, sem repetir seu nome ou qualquer prefixo.
"""

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        response = completion.choices[0].message.content.strip()
        if response.startswith(f"{npc['name']}:"):
            response = response[len(npc['name']) + 1:].strip()
    except Exception as e:
        response = f"[Erro na geração da resposta do NPC: {str(e)}]"

    detected_emotion = detect_emotion_from_message(message)

    emotion_map = {
        "grato": ("grato", "satisfeito"),
        "raiva": ("raiva", "agressivo"),
        "triste": ("triste", "melancólico"),
        "feliz": ("feliz", "alegre"),
        "sarcástico": ("raiva", "irritado"),
        "confuso": ("neutro", "confuso"),
        "calmo": ("neutro", "calmo"),
        "ansioso": ("ansioso", "nervoso"),
        "frustrado": ("raiva", "frustrado"),
        "neutro": ("neutro", "estável"),
    }

    new_emotion, new_mood = emotion_map.get(detected_emotion, ("neutro", "estável"))

    update_npc_emotion(npc['id'], new_emotion, new_mood)

    save_interaction(sender, receiver, message, response)

    insert_npc_memory(npc['id'], embed_text(message), message, memory_type="mensagem_usuario")
    insert_npc_memory(npc['id'], embed_text(response), response, memory_type="resposta_npc")

    html = format_interaction_html(sender, npc['name'], message, response)

    return {
        "from": npc["name"],
        "to": sender,
        "emotion": new_emotion,
        "mood": new_mood,
        "response": response,
        "html": html
    }
