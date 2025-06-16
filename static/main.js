async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) throw await res.json();
    return res.json();
  }

  function addStoryEntry(entry) {
    const ul = document.getElementById("story-log");
    const li = document.createElement("li");
    li.textContent = `${entry.created_at}: ${entry.entry}`;
    ul.appendChild(li);
  }

  async function loadStoryLog() {
    try {
      const log = await fetchJSON("/story_log");
      log.forEach(addStoryEntry);
    } catch {
      console.warn("Erro ao carregar histórico da narrativa.");
    }
  }

  document.getElementById("npc-form").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    if (data.tags) {
      data.tags = data.tags.split(',').map(t => t.trim());
    }
    try {
      await fetchJSON("/register_npc", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      alert("NPC cadastrado com sucesso!");
      location.reload();
    } catch (err) {
      alert("Erro ao cadastrar NPC: " + (err.message || JSON.stringify(err)));
    }
  });

  document.getElementById("interact-form").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.target;
    const data = {
      to: form.to.value,
      message: form.message.value.trim(),
      from: form.from.value.trim() || "Usuário"
    };
    const responseDiv = document.getElementById("response");
    responseDiv.textContent = "Carregando resposta...";
    try {
      const json = await fetchJSON("/interact_npc", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      responseDiv.textContent = `Resposta de ${json.from} para ${json.to}:\n${json.response}`;
    } catch (err) {
      responseDiv.textContent = "Erro: " + (err.error || JSON.stringify(err));
    }
  });

  // Busca IA - agora espera objeto único NPC
  document.getElementById("search-form").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.target;
    const query = form.query.value.trim();
    if (!query) return;
    try {
      const npc = await fetchJSON("/search_npc", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ query })
      });

      if (!npc || Object.keys(npc).length === 0) {
        alert("Nenhum NPC encontrado.");
        return;
      }

      const npcForm = document.getElementById("npc-form");

      for (const [key, value] of Object.entries(npc)) {
        const input = npcForm.elements.namedItem(key);
        if (input) {
          input.value = Array.isArray(value) ? value.join(', ') : value;
        }
      }

      alert("NPC gerado e carregado. Você pode editar antes de cadastrar.");

    } catch (err) {
      alert("Erro ao buscar NPC: " + (err.error || JSON.stringify(err)));
    }
  });

  loadStoryLog();