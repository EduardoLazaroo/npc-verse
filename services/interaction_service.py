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

    vector_memories_raw = search_npc_memories(
        npc_id=npc['id'],
        query_text=message,
        memory_types=["interacao"],
        top_k=10,
        debug=True,
        min_score=0.3
    )

    formatted_vector_memories = [f"(memória relevante) {mem['text']}" for mem in vector_memories_raw]
    print(f"[DEBUG] Memórias vetoriais selecionadas (score >= 0.3): {len(formatted_vector_memories)}")

    full_context = "\n".join(formatted_vector_memories + formatted_sql_history)
    print("\n[DEBUG] Full context being used:\n" + full_context + "\n")

    personality = npc.get("personality", "")

    prompt = f"""
Você é {npc['name']}, um personagem fictício dentro de um sistema interativo de NPCs.

### PERSONALIDADE DO PERSONAGEM:
{personality}

### ESTADO ATUAL:
Emoção: {current_emotion}
Humor: {current_mood}

### CONTEXTO RECUPERADO:
A seguir estão interações anteriores relevantes, extraídas da memória do personagem e do histórico recente de conversa.
O conteúdo inclui falas marcadas claramente com quem disse o quê:

{full_context}

### INTERAÇÃO ATUAL:
Agora, o usuário chamado \"{sender}\" diz: \"{message}\"

### INSTRUÇÕES GERAIS:
Você deve responder de forma natural, envolvente e coerente com a personalidade e experiências anteriores do personagem. Para isso:

- Entre no personagem completamente. Nunca fale como narrador ou como IA.
- Use um estilo de fala que combine com sua personalidade.
- Dê respostas completas e interessantes, evitando ser monossilábico ou robótico.
- Demonstre emoções e traços de personalidade consistentes com o personagem.
- Sempre que possível, **puxe assunto** ou estimule o usuário a continuar o diálogo.
- Evite repetir literalmente interações passadas, a não ser que seja solicitado diretamente.

### INSTRUÇÕES ESPECIAIS SOBRE REPETIÇÕES:
Se o usuário perguntar algo como “eu já perguntei isso?”, “você repetiu o que eu disse?”, “a gente já falou disso?” ou similar:

- Verifique se a pergunta do usuário **já foi feita anteriormente**.
- Se sim, responda de forma natural e contextual, reconhecendo que já conversaram sobre isso.
- Mostre **apenas a pergunta que o usuário fez anteriormente**, e **não a resposta do NPC**.
- Sempre **complete a resposta com uma continuação amigável e fluida**, por exemplo:

> “Sim! Você já me perguntou: ‘[pergunta anterior]’. Quer falar mais sobre isso ou explorar outro assunto?”

- **Nunca** responda apenas com o texto cru da pergunta anterior. Use linguagem natural, como se estivesse em uma conversa de verdade.

### FORMATO FINAL:
Responda apenas com o texto do NPC, sem prefixos como “{npc['name']}:” ou instruções adicionais. A resposta deve parecer uma fala espontânea do personagem em conversa com o usuário.
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
