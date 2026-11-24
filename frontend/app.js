"use strict";
const content = document.querySelector("#content");
const notice = document.querySelector("#notice");
const panel = document.querySelector(".workspace");
const apiUrl = window.TASK_MANAGER_CONFIG?.apiUrl?.trim();
let busy = false;
let activeAction = "";
if (apiUrl) document.querySelector("#connection").textContent = "API configured";
function message(text = "", error = false) {
  notice.textContent = text;
  notice.className = error ? "error" : "";
}
function element(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}
async function request(payload) {
  if (!apiUrl) throw new Error("Set apiUrl in frontend/config.js to your Lambda Function URL first.");
  let response;
  try {
    response = await fetch(apiUrl, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), signal: AbortSignal.timeout(20000)
    });
  } catch {
    throw new Error("Could not reach the API. Check the URL and CORS settings. If you submitted a change, list tasks before retrying; it may have succeeded.");
  }
  let data;
  try { data = await response.json(); }
  catch { throw new Error("The API returned an unreadable response. Check the deployed Lambda handler."); }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}
async function run(work) {
  if (busy) return;
  busy = true;
  panel.setAttribute("aria-busy", "true");
  document.querySelectorAll("button").forEach(button => button.disabled = true);
  message("Working…");
  try { await work(); }
  catch (error) { message(error.message, true); }
  finally {
    busy = false;
    panel.setAttribute("aria-busy", "false");
    document.querySelectorAll("button").forEach(button => button.disabled = false);
  }
}
function renderTasks(tasks, action) {
  content.replaceChildren();
  const visible = action === "complete" ? tasks.filter(task => task.status !== "complete") : tasks;
  document.querySelector("#panel-meta").textContent = `${visible.length} TASK${visible.length === 1 ? "" : "S"}`;
  if (!visible.length) {
    const empty = element("div", "", "empty");
    empty.append(element("h3", action === "complete" ? "All caught up." : "Nothing here yet."), element("p", "Create a task whenever you’re ready."));
    content.append(empty);
    return;
  }
  visible.forEach(task => {
    const row = element("article", "", "task");
    const info = element("div", "");
    info.append(element("h3", task.title), element("p", task.description || ""), element("small", task.task_id));
    row.append(info);
    if (action === "list") row.append(element("span", task.status === "complete" ? "Complete" : "To do", "badge"));
    else {
      const button = element("button", action === "delete" ? "Delete" : "Complete", action === "delete" ? "danger" : "");
      button.disabled = busy;
      button.addEventListener("click", () => {
        if (action === "delete" && !window.confirm(`Delete “${task.title}”? This cannot be undone.`)) return;
        run(async () => {
          const result = await request({action, task_id: task.task_id});
          renderTasks(tasks.filter(item => item.task_id !== task.task_id), action);
          message(result.message);
        });
      });
      row.append(button);
    }
    content.append(row);
  });
}
function renderCreate() {
  content.innerHTML = '<p class="muted">Start with a name. Add the details that help.</p><form><label for="title">Task title</label><input id="title" name="title" placeholder="What would you like to get done?" required maxlength="200"><label for="description">Description <span class="muted">(optional)</span></label><textarea id="description" name="description" placeholder="A few useful details…" maxlength="5000"></textarea><button class="primary" type="submit">Create task ＋</button></form>';
  const form = content.querySelector("form");
  form.addEventListener("submit", event => {
    event.preventDefault();
    const title = form.elements.title.value.trim();
    if (!title) { message("Enter a task title.", true); return; }
    run(async () => {
      const result = await request({action: "create", title, description: form.elements.description.value});
      form.reset();
      message(`${result.message}: ${result.task.title}`);
    });
  });
  form.elements.title.focus();
}
document.querySelectorAll("nav button").forEach(button => {
  button.addEventListener("click", () => {
    if (busy) return;
    activeAction = button.dataset.action;
    document.querySelectorAll("nav button").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    document.querySelector("#panel-title").textContent = {create:"Create a task", list:"Your tasks", complete:"Finish something", delete:"Clear some space"}[activeAction];
    document.querySelector("#panel-meta").textContent = "";
    message();
    content.replaceChildren();
    if (activeAction === "create") renderCreate();
    else run(async () => {
      const data = await request({action: "list"});
      renderTasks(data.tasks, activeAction);
      message();
    });
  });
});
