from models.db import get_db_connection

def save_npc(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO npcs (name, role, location, personality, status) VALUES (%s, %s, %s, %s, %s)",
        (data['name'], data['role'], data['location'], data['personality'], data['status'])
    )
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

def save_interaction(sender, receiver, message, response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interactions (sender, receiver, message, response) VALUES (%s, %s, %s, %s)",
        (sender, receiver, message, response)
    )
    conn.commit()
    cursor.close()
    conn.close()

def save_story_entry(entry):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO story_log (entry) VALUES (%s)", (entry,))
    conn.commit()
    cursor.close()
    conn.close()

def get_story_log():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, entry, created_at FROM story_log ORDER BY created_at DESC")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
