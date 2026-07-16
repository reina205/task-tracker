const API_BASE = "http://localhost:8000";

const board = document.getElementById("board");
const modal = document.getElementById("task-modal");
const form = document.getElementById("task-form");
const errorBanner = document.getElementById("error-banner");
const filterPriority = document.getElementById("filter-priority");

let currentTasks = [];

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  setTimeout(() => errorBanner.classList.add("hidden"), 4000);
}

// fetch() does not reject on 404/422 — it only rejects on network failure.
// Every call here must check response.ok / response.status explicitly.
async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    showError("Could not reach the server. Is the backend running?");
    throw err;
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body.detail) detail = JSON.stringify(body.detail);
    } catch {
      // response had no JSON body; keep default message
    }
    showError(detail);
    throw new Error(detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

async function fetchTasks() {
  const params = new URLSearchParams();
  if (filterPriority.value) params.set("priority", filterPriority.value);
  const query = params.toString() ? `?${params.toString()}` : "";
  currentTasks = await apiRequest(`/tasks${query}`);
  renderBoard();
}

function renderBoard() {
  const columns = { ToDo: [], InProgress: [], Done: [] };
  for (const task of currentTasks) {
    columns[task.status].push(task);
  }

  for (const status of Object.keys(columns)) {
    const list = document.getElementById(`list-${status}`);
    list.innerHTML = "";
    document.getElementById(`count-${status}`).textContent = columns[status].length;

    for (const task of columns[status]) {
      list.appendChild(renderCard(task));
    }
  }
}

function renderCard(task) {
  const card = document.createElement("div");
  card.className = "card";
  card.draggable = true;
  card.dataset.id = task.id;

  card.innerHTML = `
    <div class="card-title"></div>
    <div class="card-desc"></div>
    <div class="card-meta">
      <span class="priority-pill priority-${task.priority}"></span>
      <span class="assignee"></span>
    </div>
  `;
  card.querySelector(".card-title").textContent = task.title;
  card.querySelector(".card-desc").textContent = task.description || "";
  card.querySelector(".priority-pill").textContent = task.priority;
  card.querySelector(".assignee").textContent = task.assignee || "";

  card.addEventListener("click", () => openEditModal(task));

  card.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", task.id);
    e.dataTransfer.effectAllowed = "move";
    card.classList.add("dragging");
  });
  card.addEventListener("dragend", () => card.classList.remove("dragging"));

  return card;
}

// --- Drag and drop wiring for each column ---
document.querySelectorAll(".column").forEach((column) => {
  column.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    column.classList.add("drag-over");
  });

  column.addEventListener("dragleave", () => column.classList.remove("drag-over"));

  column.addEventListener("drop", async (e) => {
    e.preventDefault();
    column.classList.remove("drag-over");
    const taskId = e.dataTransfer.getData("text/plain");
    const newStatus = column.dataset.status;

    try {
      await apiRequest(`/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      await fetchTasks();
    } catch {
      // error already shown by apiRequest; board stays as-is
    }
  });
});

// --- Modal handling ---
function openNewModal() {
  form.reset();
  document.getElementById("task-id").value = "";
  document.getElementById("modal-title").textContent = "New Task";
  document.getElementById("delete-btn").classList.add("hidden");
  modal.showModal();
}

function openEditModal(task) {
  document.getElementById("task-id").value = task.id;
  document.getElementById("title").value = task.title;
  document.getElementById("description").value = task.description || "";
  document.getElementById("priority").value = task.priority;
  document.getElementById("assignee").value = task.assignee || "";
  document.getElementById("modal-title").textContent = "Edit Task";
  document.getElementById("delete-btn").classList.remove("hidden");
  modal.showModal();
}

document.getElementById("new-task-btn").addEventListener("click", openNewModal);
document.getElementById("cancel-btn").addEventListener("click", () => modal.close());

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("task-id").value;
  const payload = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value || null,
    priority: document.getElementById("priority").value,
    assignee: document.getElementById("assignee").value || null,
  };

  try {
    if (id) {
      await apiRequest(`/tasks/${id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    } else {
      await apiRequest("/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    }
    modal.close();
    await fetchTasks();
  } catch {
    // error already shown; keep modal open so user can fix input
  }
});

document.getElementById("delete-btn").addEventListener("click", async () => {
  const id = document.getElementById("task-id").value;
  if (!id) return;
  try {
    await apiRequest(`/tasks/${id}`, { method: "DELETE" });
    modal.close();
    await fetchTasks();
  } catch {
    // error already shown
  }
});

filterPriority.addEventListener("change", fetchTasks);

fetchTasks();
