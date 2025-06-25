CREATE DATABASE IF NOT EXISTS npcverse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE npcverse;

CREATE TABLE npcs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    origin_world VARCHAR(255),
    archetype VARCHAR(255),
    alignment VARCHAR(255),
    personality_traits TEXT,
    voice_style TEXT,
    mood VARCHAR(100),
    emotion VARCHAR(100),
    skills TEXT,
    known_for TEXT,
    catchphrase TEXT,
    backstory TEXT,
    tags TEXT,
    avatar_url TEXT
);

CREATE TABLE interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    npc_id INT,
    interaction_index INT,
    sender_role VARCHAR(20),
    user_emotion VARCHAR(50),
    npc_emotion VARCHAR(50),
    embedding_id VARCHAR(64),
    sender VARCHAR(255),
    receiver VARCHAR(255),
    message TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Story Log (histórico de narrativa)
CREATE TABLE story_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry TEXT NOT NULL, -- entrada narrativa
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);