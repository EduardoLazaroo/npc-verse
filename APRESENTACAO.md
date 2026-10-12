# Apresentacao profissional

## Identidade e valor

NPCVerse e uma aplicacao Flask para criar e conversar com NPCs persistentes em cenarios de jogos, narrativa e role-play. Combina perfis gerados por IA, estado emocional, historico relacional em SQLite e memoria semantica recuperada pelo Qdrant com embeddings SentenceTransformers.

## Texto para publicacao

> O NPCVerse investiga como tornar personagens conversacionais mais consistentes ao longo de uma narrativa. A arquitetura combina perfil e dialogo gerados por IA, estado emocional, registros relacionais e memoria semantica para recuperar contexto relevante. O desafio foi separar responsabilidades entre rotas, servicos, banco relacional e busca vetorial, evitando que cada interacao dependa apenas do ultimo prompt. O resultado e um prototipo para jogos e storytelling que evidencia escolhas de persistencia e contexto, ainda dependente de provisionamento externo do Qdrant e de validacao para uso em producao.

## Evidencias visuais recomendadas

1. Cadastro e perfil do NPC.
2. Lista de personagens.
3. Conversa com estado emocional.
4. Historico e memoria semantica recuperada.

## Prompt para imagem complementar

```text
Diagrama de arquitetura para NPCs persistentes: usuario conversa com personagem, servico de interacao consulta perfil e estado emocional, SQLite armazena historico e Qdrant recupera memorias vetoriais, modelo de linguagem gera resposta contextual; estilo de narrativa interativa sofisticada, fundo escuro discreto, sem logotipos.
```
