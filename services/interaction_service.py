from services.embedding_service import embed_text
from services.qdrant_service import insert_npc_memory, search_npc_memory
from models.npcverse_model import get_npc_by_name, save_interaction
from services.narrator_service import contextualize_interaction
from services.story_service import narrate_and_log

def process_interaction(data):
    sender = data['from']
    receiver = data['to']
    message = data['message']

    npc = get_npc_by_name(receiver)
    if not npc:
        return {"error": f"NPC '{receiver}' não encontrado"}

    # Vetoriza a mensagem
    query_vector = embed_text(message)

    # Busca memórias relevantes
    memory = search_npc_memory(npc['id'], query_vector)

    # Narrador contextualiza
    response = contextualize_interaction(sender, npc['name'], message, memory)
    narrate_and_log(sender, npc['name'], message, response)

    # Armazena no banco
    save_interaction(sender, receiver, message, response)

    # Armazena no Qdrant também
    insert_npc_memory(npc['id'], query_vector, message)

    return {
        "from": npc["name"],
        "to": sender,
        "emotion": "neutro",
        "response": response,
        "memory_match": memory
    }
