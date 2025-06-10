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

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def process_interaction(data):
    sender = data['from']
    receiver = data['to']
    message = data['message']

    npc = get_npc_by_name(receiver)
    if not npc:
        return {"error": f"NPC '{receiver}' não encontrado"}

    npc_state = get_npc_state(npc['id'])
    emotion = npc_state.get("emotion", "neutro")
    mood = npc_state.get("mood", "estável")

    # 📘 Recuperação híbrida: últimas 10 interações (SQL) + 3 memórias relevantes (Qdrant)
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
    formatted_vector_memories = [
        f"(memória relevante) {mem}" for mem in vector_memories
    ]

    full_context = "\n".join(formatted_vector_memories + formatted_sql_history)

    personality = npc.get("personality", "")
    prompt = f"""
Você é {npc['name']}, um NPC com a seguinte personalidade: {personality}.
Seu estado emocional atual é {emotion} e seu humor está {mood}.

Contexto recuperado da memória:
{full_context}

Agora {sender} diz: "{message}"

Responda de forma coerente com sua personalidade, humor e todo o contexto da conversa.
"""

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        response = completion.choices[0].message.content.strip()
    except Exception as e:
        response = f"[Erro na geração da resposta do NPC: {str(e)}]"

    # Atualiza emoção simples
    if "obrigado" in message.lower():
        update_npc_emotion(npc['id'], "grato", "satisfeito")
    elif "odeio" in message.lower():
        update_npc_emotion(npc['id'], "raiva", "agressivo")
    else:
        update_npc_emotion(npc['id'], "neutro", "estável")

    save_interaction(sender, receiver, message, response)

    story_entry = f"{sender} falou com {receiver}: \"{message}\"\n{receiver} respondeu: \"{response}\""
    save_story_entry(story_entry)

    # 🧠 Salva as memórias
    insert_npc_memory(npc['id'], embed_text(message), message, memory_type="mensagem_usuario")
    insert_npc_memory(npc['id'], embed_text(response), response, memory_type="resposta_npc")

    return {
        "from": npc["name"],
        "to": sender,
        "emotion": emotion,
        "response": response
    }
