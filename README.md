# 🧠 NPCVerse – NPCs Interativos com Memória, Emoção e Personalidade

O **NPCVerse** é uma aplicação web que permite criar, interagir e evoluir **NPCs inteligentes** com **memória híbrida**, **personalidade persistente** e **emoções dinâmicas**, utilizando o poder da **IA generativa**, **embeddings vetoriais** e **modelos da OpenAI**.

![NPCVerse Banner](https://i.postimg.cc/YSmj2fL0/npcverse-banner.png)

---

## ✨ Funcionalidades

- 🧬 **Criação de NPCs** via prompts inteligentes com **GPT-4**
- 💾 **Armazenamento híbrido**: banco relacional (**SQLite**) + memória semântica vetorial (**Qdrant**)
- 🧠 **Emoções dinâmicas** com detecção e decaimento automático
- 🗣️ **Interação contextualizada** com:
  - Últimas **10 interações** salvas no banco SQL
  - **3 memórias vetoriais relevantes** recuperadas por similaridade
  - **Perfil e estado emocional** atual do NPC
- 🎭 **Personalidade persistente** baseada em traços e histórico individual
- 🌐 Interface web com cadastro, histórico de conversa e avatar

---

## 🛠️ Tecnologias Utilizadas

| Camada           | Tecnologias                                                                 |
|------------------|------------------------------------------------------------------------------|
| Backend          | [Python](https://www.python.org/), [Flask](https://flask.palletsprojects.com/) |
| Banco de Dados   | [SQLite](https://www.sqlite.org/)                                            |
| Vetores Semânticos| [Qdrant](https://qdrant.tech/) (armazenamento e busca por similaridade)     |
| Embeddings       | [SentenceTransformers - all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| IA Generativa    | [OpenAI GPT-4o](https://openai.com/gpt-4)                                    |
| Frontend         | HTML, CSS custom, JavaScript Vanilla                                         |
| Configuração     | [python-dotenv](https://pypi.org/project/python-dotenv/)                     |
| Hospedagem       | Localhost (modo desenvolvimento)                                             |

---

## 🧪 Como Rodar Localmente

### ✅ Pré-requisitos

- Python 3.10+
- Conta com acesso à API da OpenAI
- Instância local ou hospedada do Qdrant (você pode usar Docker)
- Chaves de API configuradas

### 🔧 Instalação

```bash
git clone https://github.com/seunome/npcverse.git
cd npcverse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
⚙️ Configuração
Crie um arquivo .env com o seguinte conteúdo:

env

OPENAI_API_KEY=your_openai_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # se necessário
🚀 Executar
bash

python app.py
Abra no navegador: http://localhost:5000
