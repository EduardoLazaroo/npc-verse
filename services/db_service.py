import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def register_npc_db(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO npcs (name, role, location, personality, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['name'], data['role'], data['location'], data['personality'], data['status']))
    conn.commit()
    npc_id = cursor.lastrowid
    conn.close()
    return npc_id

def get_all_npcs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs")
    npcs = cursor.fetchall()
    conn.close()
    return npcs

def get_npc_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM npcs WHERE name = %s", (name,))
    npc = cursor.fetchone()
    conn.close()
    return npc
