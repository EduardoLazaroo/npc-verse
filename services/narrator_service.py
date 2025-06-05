from models.npcverse_model import get_npc_state

def contextualize_interaction(sender, receiver, message, memory, npc_id):
    state = get_npc_state(npc_id)
    emotion = state.get("emotion", "neutro")
    mood = state.get("mood", "estável")

    if memory:
        return f"{receiver} ({emotion}, {mood}) lembra: \"{memory['text']}\" e responde a {sender} com base nisso."
    else:
        return f"{receiver} ({emotion}, {mood}) não se lembra de nada relevante, mas responde com neutralidade a {sender}."
