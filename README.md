🧠 NPCVerse — Sistema de NPCs Interativos com Memória Híbrida
O NPCVerse é um sistema backend que permite a criação de NPCs interativos com personalidade, emoções variáveis e capacidade de lembrar interações anteriores. Ele combina recuperação simbólica (SQL) com memória semântica vetorial (Qdrant) para construir um modelo conversacional mais realista e imersivo.

⚙️ Tecnologias Utilizadas
Flask (Python): Backend RESTful modularizado por routes, models e services.

MySQL: Armazena dados estruturados (NPCs, emoções, histórico, interações).

Qdrant: Banco vetorial para memórias semânticas com filtro por tipo, NPC e recência.

OpenAI GPT-4o-mini: Geração de respostas personalizadas com base no estado emocional e contexto.

Sentence Transformers (all-MiniLM-L6-v2): Conversão de texto em embeddings vetoriais.

dotenv: Gerenciamento seguro de variáveis sensíveis.

🧩 Funcionalidades Chave
Memória híbrida de contexto:

Últimas 10 interações (SQL) → memória de curto prazo.

3 memórias semânticas mais relevantes (Qdrant) → memória de longo prazo.

Personalidade e estado emocional dinâmico:

Cada NPC tem traços de personalidade definidos.

Emoções e humor mudam com base nas interações.

Interação narrativa:

Cada diálogo é registrado em um story_log com linguagem natural.

Prompt dinâmico inteligente:

A construção do prompt do LLM combina: personalidade, humor, memória híbrida e nova mensagem.

🧠 Arquitetura Cognitiva Simulada
O projeto simula aspectos de cognição artificial:

Integra memória episódica e semântica.

Gera comportamento linguístico afetado por emoção.

Permite diálogos consistentes e adaptativos ao longo do tempo.