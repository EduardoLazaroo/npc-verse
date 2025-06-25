from models.npcverse_model import (
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
    formatted_sql_history = []
    for entry in sql_history:
        formatted_sql_history.append(f"[USUÁRIO] {entry['sender']} disse: \"{entry['message']}\"")
        formatted_sql_history.append(f"[NPC] {entry['receiver']} respondeu: \"{entry['response']}\"")

    vector_memories = search_npc_memories(
        npc_id=npc['id'],
        query_text=message,
        memory_types=["interacao"],
        top_k=5,
        debug=True
    )
    formatted_vector_memories = [f"(memória relevante) {mem}" for mem in vector_memories]

    full_context = "\n".join(formatted_vector_memories + formatted_sql_history)

    print("\n[DEBUG] Full context being used:\n" + full_context + "\n")

    personality = npc.get("personality", "")

    prompt = f"""
Você é {npc['name']}, um NPC com a seguinte personalidade: {personality}.
Seu estado emocional atual é {current_emotion} e seu humor está {current_mood}.

Contexto recuperado da memória (com marcações claras de quem falou o quê):
{full_context}

Agora, o usuário chamado \"{sender}\" diz: \"{message}\"

INSTRUÇÃO IMPORTANTE:
- Se a pergunta do usuário for para saber qual foi a pergunta que ele fez em alguma interação passada, responda **APENAS** com o texto da pergunta feita pelo usuário naquela interação, sem responder com a fala do NPC.
- Se a pergunta do usuário for qualquer outra coisa, responda normalmente com o texto do NPC, sem prefixos ou nomes.
- Nunca responda com o texto de uma fala do NPC quando o usuário pedir pela pergunta feita por ele.

Responda apenas o texto da fala apropriada de acordo com essas regras.
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

    user_emotion = detect_emotion_from_message(message)
    npc_emotion = detect_emotion_from_message(response)

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

    new_emotion, new_mood = emotion_map.get(npc_emotion, ("neutro", "estável"))

    update_npc_emotion(npc['id'], new_emotion, new_mood)

    existing_interactions = get_interactions_with_npc(receiver)
    interaction_index = len(existing_interactions) + 1

    full_interaction_text = f'{sender}: "{message}"\n{npc["name"]}: "{response}"'
    embedding_vector = embed_text(full_interaction_text)

    embedding_id = insert_npc_memory(
        npc_id=npc['id'],
        vector=embedding_vector,
        text=full_interaction_text,
        memory_type="interacao",
        metadata={
            "sender": sender,
            "receiver": npc['name'],
            "interaction_index": interaction_index,
            "user_emotion": user_emotion,
            "npc_emotion": npc_emotion,
        }
    )
    save_interaction(
        sender=sender,
        npc_name=npc['name'],
        message=message,
        response=response,
        npc_id=npc['id'],
        interaction_index=interaction_index,
        sender_role="user",
        user_emotion=user_emotion,
        npc_emotion=npc_emotion,
        embedding_id=embedding_id
    )


    html = format_interaction_html(sender, npc['name'], message, response)

    return {
        "from": npc["name"],
        "to": sender,
        "emotion": new_emotion,
        "mood": new_mood,
        "response": response,
        "html": html
    }
