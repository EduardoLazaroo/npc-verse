# Apresentação Profissional: NPCVerse

## 1. Identidade e Proposta de Valor

O **NPCVerse** é uma solução de arquitetura cognitiva aplicada a jogos digitais e experiências narrativas interativas. O projeto resolve a limitação fundamental de NPCs convencionais — que costumam ser estáticos, repetitivos ou esquecer o contexto pregressos das conversas — por meio de uma **arquitetura híbrida de memória e modulação emocional**.

Ao acoplar **persistência relacional em MySQL 8.0** para controle determinístico de estados e inventários narrativos, **banco vetorial Qdrant** para memória episódica associativa indexada em 384 dimensões e modelos de linguagem generativos, o sistema viabiliza personagens que lembram de promessas feitas pelo jogador, reagem emocionalmente a eventos e preservam traços psicológicos consistentes.

---

## 2. Destaques Técnicos e Decisões de Arquitetura

1. **Separação de Memória de Curto e Longo Prazo**: Em vez de injetar cegamente milhares de tokens na janela de contexto de LLMs, o backend orquestra uma janela deslizante das últimas interações (MySQL) combinada com recuperação k-NN das memórias mais relevantes via Qdrant (`Cosine Distance` com índice HNSW).
2. **Eficiência Computacional com Embeddings Locais**: A vetorização de falas e fatos utiliza o modelo `all-MiniLM-L6-v2` via `sentence-transformers`, eliminando custos e latência de rede para geração de embeddings vetoriais.
3. **Modulação de Humor e Emoções**: A cada turno conversacional, além de sintetizar a réplica, o sistema calcula a transição de afeto (*mood* e *emotion*), refletindo a dinâmica psicológica do personagem na base de dados relacional.
4. **Resiliência e Fallbacks**: O pipeline foi desenhado com desacoplamento modular; se a base vetorial sofrer degradação temporária, o motor continua respondendo com base no histórico relacional e perfil estruturado.

---

## 3. Texto Executivo para Divulgação / Portfólio

> "Personagens secundários em jogos digitais frequentemente sofrem de amnésia contextual ou comportamento mecânico previsível. No projeto **NPCVerse**, desenvolvi uma arquitetura híbrida de agentes cognitivos combinando **Flask**, **MySQL 8.0**, **Qdrant Vector DB** e modelos de linguagem avançados.
>
> O sistema implementa uma camada de memória semântica vetorial em 384 dimensões (`all-MiniLM-L6-v2`) operando em conjunto com histórico episódico estruturado em banco relacional. Cada interação do jogador desencadeia busca por similaridade semântica para recuperar fatos relevantes passados, modula os estados emocionais do personagem e gera respostas alinhadas à sua persona.
>
> A validação prática do ambiente integrado atestou tempo de resposta ágil, recuperação semântica consistente (score cosseno > 0.55 em memórias correlatas) e persistência íntegra do ciclo conversacional."

---

## 4. Evidências Empíricas e Visuais Disponíveis

- [`evidencias/arquitetura_npc_verse.png`](evidencias/arquitetura_npc_verse.png): Diagrama de blocos das camadas de frontend, API Flask, banco relacional MySQL e índice vetorial Qdrant.
- [`evidencias/fluxo_emocional_memoria_npc.png`](evidencias/fluxo_emocional_memoria_npc.png): Mapa do fluxo em 5 etapas desde a fala do usuário até a modulação de humor e indexação de memória.
- [`evidencias/log_execucao_real.txt`](evidencias/log_execucao_real.txt): Registro fidedigno da criação das tabelas MySQL, inicialização da coleção Qdrant, inserção dos embeddings e teste com TestClient HTTP.
