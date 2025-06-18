from models.db import get_db_connection

def save_npc(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO npcs
    (name, origin_world, archetype, alignment, personality_traits, voice_style,
    mood, emotion, skills, known_for, catchphrase, backstory, tags, avatar_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data.get('name'),
        data.get('origin_world'),
        data.get('archetype'),
        data.get('alignment'),
        data.get('personality_traits'),
        data.get('voice_style'),
        data.get('mood'),
        data.get('emotion'),
        data.get('skills'),
        data.get('known_for'),
        data.get('catchphrase'),
        data.get('backstory'),
        ",".join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags'),
        data.get('avatar_url')
    ))

    conn.commit()
    cursor.close()
    conn.close()

def get_all_npcs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM npcs")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_npc_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM npcs WHERE name = %s", (name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def save_interaction(sender, npc_name, message, response):
    """Salva interação somente na tabela interactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interactions (sender, receiver, message, response) VALUES (%s, %s, %s, %s)",
        (sender, npc_name, message, response)
    )
    conn.commit()
    cursor.close()
    conn.close()

def save_story_entry(entry, npc_name=None):
    """Salva entrada no log de narrativa"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if npc_name:
        cursor.execute("INSERT INTO story_log (entry, npc_name) VALUES (%s, %s)", (entry, npc_name))
    else:
        cursor.execute("INSERT INTO story_log (entry) VALUES (%s)", (entry,))
    conn.commit()
    cursor.close()
    conn.close()

def get_interactions_with_npc(npc_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM interactions WHERE receiver = %s ORDER BY id ASC", (npc_name,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_story_log_by_npc(npc_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, entry, created_at 
        FROM story_log 
        WHERE npc_name = %s 
        ORDER BY created_at DESC
    """, (npc_name,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def update_npc_emotion(npc_id, emotion, mood=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE npcs SET emotion = %s, mood = %s WHERE id = %s"
    cursor.execute(sql, (emotion, mood, npc_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_npc_state(npc_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT emotion, mood FROM npcs WHERE id = %s", (npc_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
