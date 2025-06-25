async function fetchJSON(url, options) { 
  const res = await fetch(url, options);
  if (!res.ok) throw await res.json();
  return res.json();
}

// 1. Busca por IA
document.getElementById("search-form").addEventListener("submit", async e => {
  e.preventDefault();
  const form = e.target;
  const query = form.query.value.trim();
  if (!query) return;

  try {
    const npc = await fetchJSON("/search_npc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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

// 2. Cadastro de NPC
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    alert("NPC cadastrado com sucesso!");
    location.reload();
  } catch (err) {
    alert("Erro ao cadastrar NPC: " + (err.message || JSON.stringify(err)));
  }
});

// 3. Interação com NPC
document.getElementById("interact-form").addEventListener("submit", async e => {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector("button[type=submit]");
  submitBtn.disabled = true;

  const to = document.getElementById("npc-select").value;
  const message = form.message.value.trim();
  const from = form.from.value.trim() || "Usuário";

  if (!to || !message) {
    alert("Preencha o nome do NPC e a mensagem.");
    submitBtn.disabled = false;
    return;
  }

  try {
    const json = await fetchJSON("/interact_npc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ from, to, message })
    });

    if (json.html) {
      const ul = document.getElementById("story-log");
      ul.innerHTML += json.html;
      ul.scrollTop = ul.scrollHeight;
    }

  } catch (err) {
    alert("Erro: " + (err.error || JSON.stringify(err)));
  } finally {
    form.reset();
    submitBtn.disabled = false;
  }
});

// 4. Histórico da narrativa
function addStoryEntry(entry) {
  const ul = document.getElementById("story-log");
  const li = document.createElement("li");
  li.innerHTML = entry.html;
  ul.appendChild(li);
}

async function loadStoryLog(npcName = null) {
  const ul = document.getElementById("story-log");
  ul.innerHTML = "";

  if (!npcName) return;

  try {
    const log = await fetchJSON(`/story_log?npc_name=${encodeURIComponent(npcName)}`);
    if (log.length === 0) {
      const li = document.createElement("li");
      li.textContent = "Nenhum histórico encontrado para este NPC.";
      ul.appendChild(li);
      return;
    }
    log.forEach(addStoryEntry);
    ul.scrollTop = ul.scrollHeight;
  } catch {
    const li = document.createElement("li");
    li.textContent = "Erro ao carregar histórico da narrativa.";
    ul.appendChild(li);
  }
}

document.getElementById('npc-select').addEventListener('change', async function () {
    const npcName = this.value;

    if (!npcName) return;

    try {
      const npc = await fetchJSON(`/npc/${encodeURIComponent(npcName)}`);

      // Exibe a interface de NPC
      document.getElementById("npc-display").style.display = "block";

      document.getElementById("npc-name-display").textContent = npc.name;
      document.getElementById("npc-avatar").src = npc.avatar_url;

      document.getElementById("npc-origin").textContent = npc.origin_world || "";
      document.getElementById("npc-archetype").textContent = npc.archetype || "";
      document.getElementById("npc-alignment").textContent = npc.alignment || "";
      document.getElementById("npc-traits").textContent = npc.personality_traits || "";
      document.getElementById("npc-voice").textContent = npc.voice_style || "";
      document.getElementById("npc-mood").textContent = npc.mood || "";
      document.getElementById("npc-emotion").textContent = npc.emotion || "";
      document.getElementById("npc-skills").textContent = npc.skills || "";
      document.getElementById("npc-known").textContent = npc.known_for || "";
      document.getElementById("npc-catchphrase").textContent = npc.catchphrase || "";
      document.getElementById("npc-backstory").textContent = npc.backstory || "";
      document.getElementById("npc-tags").textContent = Array.isArray(npc.tags) ? npc.tags.join(', ') : npc.tags || "";

      loadStoryLog(npcName);
    } catch (err) {
      alert("Erro ao buscar dados do NPC: " + (err.error || JSON.stringify(err)));
    }
  });


loadStoryLog();
