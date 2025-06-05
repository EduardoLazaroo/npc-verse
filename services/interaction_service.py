from services.embedding_service import embed_text
from services.qdrant_service import insert_npc_memory, search_npc_memory
from models.npcverse_model import get_npc_by_name, save_interaction, update_npc_emotion, get_npc_state
from services.narrator_service import contextualize_interaction
from services.story_service import narrate_and_log

def process_interaction(data):
    sender = data['from']
    receiver = data['to']
    message = data['message']

    npc = get_npc_by_name(receiver)
    if not npc:
        return {"error": f"NPC '{receiver}' não encontrado"}

    query_vector = embed_text(message)
    memory = search_npc_memory(npc['id'], query_vector)

    response = contextualize_interaction(sender, npc['name'], message, memory, npc['id'])

    # Emoção baseada na mensagem
    if "obrigado" in message.lower():
        update_npc_emotion(npc['id'], "grato", "satisfeito")
    elif "odeio" in message.lower():
        update_npc_emotion(npc['id'], "raiva", "agressivo")
    else:
        update_npc_emotion(npc['id'], "neutro", "estável")

    npc_state = get_npc_state(npc['id'])
    emotion = npc_state.get("emotion", "neutro")

    narrate_and_log(sender, npc['name'], message, response)
    save_interaction(sender, receiver, message, response)
    insert_npc_memory(npc['id'], query_vector, message, memory_type="interaction")

    return {
        "from": npc["name"],
        "to": sender,
        "emotion": emotion,
        "response": response,
        "memory_match": memory
    }
