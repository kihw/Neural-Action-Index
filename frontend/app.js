const state = {
  query: "",
  selectedId: null,
  selectedResource: null,
  resolveResponse: null,
  searchResults: [],
  path: { search: false, open: false, resolve: false, link: false },
};

const els = {
  searchInput: document.getElementById("search-input"),
  searchBtn: document.getElementById("search-btn"),
  searchResults: document.getElementById("search-results"),
  tree: document.getElementById("tree"),
  resourceTitle: document.getElementById("resource-title"),
  preview: document.getElementById("preview-content"),
  resourceForm: document.getElementById("resource-form"),
  matchReasons: document.getElementById("match-reasons"),
  relatedList: document.getElementById("related-list"),
  resolveTrace: document.getElementById("resolve-trace"),
  openBtn: document.getElementById("open-btn"),
  resolveBtn: document.getElementById("resolve-btn"),
  linkBtn: document.getElementById("link-btn"),
};

let editor;

function initMonaco() {
  return new Promise((resolve) => {
    window.require.config({
      paths: {
        vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs",
      },
    });

    window.require(["vs/editor/editor.main"], () => {
      editor = monaco.editor.create(document.getElementById("editor"), {
        value: "# Source YAML apparaîtra ici",
        language: "yaml",
        theme: "vs-dark",
        minimap: { enabled: false },
        automaticLayout: true,
      });
      resolve();
    });
  });
}

async function api(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }
  return response.json();
}

function toYAML(resource) {
  const lines = [
    `id: ${resource.id}`,
    `type: ${resource.type}`,
    `title: ${resource.title}`,
    `category: ${resource.category}`,
    `theme: ${resource.theme}`,
    `description: ${resource.description}`,
    `content_ref: ${resource.content_ref}`,
    "variables:",
    ...resource.variables.map((v) => `  - name: ${v.name}\n    kind: ${v.kind}\n    required: ${v.required}`),
    `tags: [${resource.tags.join(", ")}]`,
    `related: [${resource.related.join(", ")}]`,
  ];
  return lines.join("\n");
}

function setPathStep(step, value) {
  state.path[step] = value;
  ["search", "open", "resolve", "link"].forEach((name) => {
    const li = document.getElementById(`step-${name}`);
    li.classList.toggle("path-complete", state.path[name]);
  });
}

function renderSearchResults() {
  els.searchResults.innerHTML = "";
  state.searchResults.forEach((result) => {
    const div = document.createElement("div");
    div.className = "list-item";
    div.innerHTML = `<strong>${result.title}</strong><br /><small>${result.id} · score ${result.score.toFixed(2)}</small>`;
    div.addEventListener("click", () => selectResult(result.id));
    els.searchResults.appendChild(div);
  });
}

function computeMatchReasons(resource) {
  const tokens = state.query.toLowerCase().split(/\s+/).filter(Boolean);
  const reasons = [];

  for (const token of tokens) {
    if (resource.title.toLowerCase().includes(token)) reasons.push(`Token "${token}" trouvé dans le titre.`);
    if (resource.description.toLowerCase().includes(token)) reasons.push(`Token "${token}" trouvé dans la description.`);
    if (resource.tags.some((tag) => tag.toLowerCase().includes(token))) reasons.push(`Token "${token}" trouvé dans les tags.`);
    if (`${resource.category} ${resource.theme}`.toLowerCase().includes(token)) reasons.push(`Token "${token}" trouvé dans catégorie/thème.`);
    if (resource.id.toLowerCase().includes(token)) reasons.push(`Token "${token}" trouvé dans l'identifiant.`);
  }

  return [...new Set(reasons)];
}

function renderMatchReasons(resource) {
  const reasons = computeMatchReasons(resource);
  els.matchReasons.innerHTML = "";
  if (reasons.length === 0) {
    els.matchReasons.innerHTML = "<li>Aucune raison explicite (match lexical global).</li>";
    return;
  }

  reasons.forEach((reason) => {
    const li = document.createElement("li");
    li.textContent = reason;
    els.matchReasons.appendChild(li);
  });
}

function renderForm(resource) {
  const fields = ["id", "type", "title", "category", "theme", "description", "content_ref"];
  els.resourceForm.innerHTML = "";

  fields.forEach((field) => {
    const label = document.createElement("label");
    label.textContent = field;
    const input = field === "description" ? document.createElement("textarea") : document.createElement("input");
    input.value = resource[field] ?? "";
    label.appendChild(input);
    els.resourceForm.appendChild(label);
  });
}

function setSelectedResource(data) {
  state.selectedResource = data.resource;
  state.selectedId = data.resource.id;
  els.resourceTitle.textContent = `${data.resource.title} (${data.resource.id})`;
  editor.setValue(toYAML(data.resource));
  renderForm(data.resource);
  renderMatchReasons(data.resource);
  els.openBtn.disabled = false;
  els.resolveBtn.disabled = false;
  els.linkBtn.disabled = data.resource.related.length === 0;
}

async function selectResult(id) {
  const data = await api(`/resource/${id}`);
  setSelectedResource(data);
}

async function runSearch() {
  const query = els.searchInput.value.trim();
  if (!query) return;
  state.query = query;
  const results = await api(`/search?q=${encodeURIComponent(query)}&limit=20`);
  state.searchResults = results.results;
  renderSearchResults();
  setPathStep("search", true);
}

async function loadTree() {
  const treeData = await api("/tree");
  const root = document.createElement("ul");

  Object.entries(treeData).forEach(([category, themes]) => {
    const categoryLi = document.createElement("li");
    categoryLi.textContent = category;
    const themesUl = document.createElement("ul");

    Object.entries(themes).forEach(([theme, ids]) => {
      const themeLi = document.createElement("li");
      themeLi.textContent = `${theme} (${ids.length})`;
      themesUl.appendChild(themeLi);
    });

    categoryLi.appendChild(themesUl);
    root.appendChild(categoryLi);
  });

  els.tree.innerHTML = "";
  els.tree.appendChild(root);
}

async function resolveSelected() {
  if (!state.selectedId) return;
  const response = await api(`/resolve/${state.selectedId}`);
  state.resolveResponse = response;
  els.preview.textContent = response.resolved_content ?? "Pas de contenu résolu.";
  els.resolveTrace.innerHTML = "";
  response.trace.forEach((item) => {
    const li = document.createElement("li");
    li.className = "trace-item";
    li.textContent = `${item.source}: ${item.detail}`;
    els.resolveTrace.appendChild(li);
  });
  setPathStep("resolve", true);
}

async function linkRelated() {
  if (!state.selectedId) return;
  const related = await api(`/related/${state.selectedId}`);
  els.relatedList.innerHTML = "";
  related.results.forEach((item) => {
    const li = document.createElement("li");
    li.className = "related-item";
    li.textContent = `${item.id} — ${item.title}`;
    els.relatedList.appendChild(li);
  });
  setPathStep("link", true);
}

function setupModes() {
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.dataset.mode;
      document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
      document.getElementById(`${mode}-view`).classList.add("active");
    });
  });
}

function setupActions() {
  els.searchBtn.addEventListener("click", runSearch);
  els.searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") runSearch();
  });

  els.openBtn.addEventListener("click", () => {
    if (state.selectedResource) {
      setPathStep("open", true);
    }
  });

  els.resolveBtn.addEventListener("click", resolveSelected);
  els.linkBtn.addEventListener("click", linkRelated);
}

await initMonaco();
setupModes();
setupActions();
loadTree();
