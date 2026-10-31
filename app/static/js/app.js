/* Creator Pulse frontend: vanilla JS, no build step, no external dependencies. */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(n || 0);
const PLAT = { youtube: { label: "YouTube", cls: "yt" }, instagram: { label: "Instagram", cls: "ig" }, facebook: { label: "Facebook", cls: "fb" } };
const state = { platform: "all", window: "7d", metric: "views", acct: null, tab: "strategy" };

async function api(path, opts) {
  const r = await fetch(path, opts);
  let data = null;
  try { data = await r.json(); } catch (_) { /* no body */ }
  if (!r.ok) {
    const d = data && data.detail;
    throw new Error(typeof d === "string" ? d : "Request failed (" + r.status + ")");
  }
  return data;
}
const send = (path, body, method = "POST") =>
  api(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), 2600);
}
const initials = (n) => n.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
const srcBadge = (o) => (o.source === "gemma"
  ? `<span class="src gemma">● Gemma · ${esc(o.model)}</span>`
  : `<span class="src">● Offline fallback (set GEMINI_API_KEY for Gemma)</span>`);

/* ------------------------------------------------------------ leaderboard */
async function loadBoard() {
  const table = $("#board"); table.classList.add("loading");
  try {
    const q = new URLSearchParams({ platform: state.platform, window: state.window, metric: state.metric });
    const data = await api("/api/leaderboard?" + q);
    renderStats(data.rows); renderRows(data.rows);
  } catch (e) { toast(e.message); }
  table.classList.remove("loading");
}

function renderStats(rows) {
  const views = rows.reduce((a, r) => a + r.views, 0);
  const gain = rows.reduce((a, r) => a + r.follower_gain, 0);
  const lead = rows[0];
  $("#stats").innerHTML = [
    ["Total views", fmt(views), "in selected window"],
    ["Follower gain", "+" + fmt(gain), "new followers"],
    ["Accounts", rows.length, "on the leaderboard"],
    ["Current leader", lead ? esc(lead.account.display_name) : "-", lead ? PLAT[lead.account.platform].label : ""],
  ].map(([l, v, s]) => `<div class="stat"><small>${l}</small><b>${v}</b><span>${s}</span></div>`).join("");
  $("#th-views").classList.toggle("strong", state.metric === "views");
  $("#th-gain").classList.toggle("strong", state.metric === "conversions");
}

function chg(n) {
  if (n > 0) return `<span class="up">▲ ${n}</span>`;
  if (n < 0) return `<span class="down">▼ ${Math.abs(n)}</span>`;
  return `<span class="same">–</span>`;
}

function renderRows(rows) {
  $("#empty").hidden = rows.length > 0;
  $("#rows").innerHTML = rows.map((r) => {
    const a = r.account, p = PLAT[a.platform];
    return `<tr class="row p${r.rank}" data-id="${esc(a.id)}">
      <td class="rank">${r.rank}</td>
      <td class="chg">${chg(r.rank_change)}</td>
      <td><div class="acct"><span class="avatar ${p.cls}">${esc(initials(a.display_name))}</span>
        <div><div class="name">${esc(a.display_name)}</div>
        <div class="handle">${esc(a.handle)} <span class="chip ${p.cls}">${p.label}</span>
        ${a.data_source === "youtube_api" ? '<span class="chip live">live</span>' : ""}
        <span>· ${fmt(a.followers)} followers</span></div></div></div></td>
      <td class="num ${state.metric === "views" ? "strong" : ""}">${fmt(r.views)}</td>
      <td class="num ${state.metric === "conversions" ? "strong" : ""}">+${fmt(r.follower_gain)}</td>
      <td class="col-top">${r.top_post ? `<div class="t">${esc(r.top_post.title)}</div>${fmt(r.top_post.views)} views` : "-"}</td>
      <td><button class="icon" data-remove="${esc(a.id)}" title="Remove account" aria-label="Remove ${esc(a.display_name)}">✕</button></td></tr>`;
  }).join("");
}

/* ------------------------------------------------------------ drawer */
async function openDrawer(id) {
  try { state.acct = await api("/api/accounts/" + encodeURIComponent(id)); } catch (e) { return toast(e.message); }
  const a = state.acct, p = PLAT[a.platform];
  $("#drawer-title").innerHTML = `<h2>${esc(a.display_name)}</h2><p>${esc(a.handle)} · <span class="chip ${p.cls}">${p.label}</span> · ${fmt(a.followers)} followers</p>`;
  $("#drawer").hidden = false; $("#scrim").hidden = false;
  setTab("strategy");
}
function closeDrawer() { $("#drawer").hidden = true; $("#scrim").hidden = true; state.acct = null; }

function setTab(tab) {
  state.tab = tab;
  $$("#drawer-tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === tab));
  tab === "strategy" ? renderStrategyTab() : renderPostsTab();
}

const bar = (label, pct) => `<div class="bar"><span>${esc(label)}</span><div class="track"><i style="width:${Math.min(+pct, 100)}%"></i></div><b>${pct}%</b></div>`;

function renderStrategyTab() {
  const a = state.acct, aud = a.audience;
  const audHtml = aud
    ? `<div class="card"><h3>Audience (from platform analytics)</h3>
        ${Object.entries(aud.gender_split).map(([k, v]) => bar(k, v)).join("")}
        <div style="height:8px"></div>
        ${Object.entries(aud.age_buckets).map(([k, v]) => bar(k, v)).join("")}
        <div style="height:8px"></div>
        ${aud.top_countries.map((c) => bar(c.country, c.pct)).join("")}</div>`
    : `<div class="card"><h3>Audience</h3><p>Demographics are unavailable for this account. Platforms only share them with the account owner via OAuth.</p></div>`;
  $("#drawer-body").innerHTML = audHtml + `
    <div class="card"><div class="ai-head"><h3 style="margin:0">AI channel strategy</h3>
      <button class="btn primary" data-action="strategy">✦ Generate strategy</button></div>
      <div id="ai-strategy"><p class="src">Gemma analyses this audience and the top posts, then recommends what to create next.</p></div></div>
    <div class="card"><div class="ai-head"><h3 style="margin:0">Content ideas</h3>
      <button class="btn" data-action="channel-ideas">✦ Generate ideas</button></div>
      <div id="ai-ideas"><p class="src">Scripts and hooks based on this channel's top performers.</p></div></div>`;
}

const loading = () => '<div class="skeleton"></div><div class="skeleton" style="width:80%"></div><div class="skeleton" style="width:60%"></div>';
const list = (arr) => `<ul>${(arr || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`;

function strategyHtml(s) {
  const ap = s.audience_profile;
  return `<div class="ai-head"><b>${esc(ap.primary_segment)}</b>${srcBadge(s)}</div>
    <div class="chips" style="margin-bottom:10px">${ap.key_traits.map((t) => `<span class="chip t">${esc(t)}</span>`).join("")}</div>
    <p class="src" style="margin:0 0 4px">Inferred interests (AI estimate, not platform data)</p>
    <div class="chips" style="margin-bottom:14px">${ap.inferred_interests.map((t) => `<span class="chip t">${esc(t)}</span>`).join("")}</div>
    <p class="src" style="margin:0 0 4px">What worked</p>${list(s.what_worked)}
    <p class="src" style="margin:14px 0 6px">What to create next</p>
    ${s.recommendations.map((r) => `<div class="rec"><b>${esc(r.format)}: ${esc(r.topic)}</b><q>“${esc(r.hook)}”</q><span class="src">${esc(r.why)}</span></div>`).join("")}
    <p class="src" style="margin:14px 0 4px">Posting advice</p><p>${esc(s.posting_advice)}</p>
    <div class="card conclusion" style="margin-top:12px"><h3>Conclusion</h3><p style="margin:0">${esc(s.conclusion)}</p></div>`;
}

function ideasHtml(r) {
  return `<div class="ai-head"><span class="src">${esc(r.scope)}</span>${srcBadge(r)}</div>` +
    r.ideas.map((i) => `<div class="idea card"><h4>${esc(i.title)}</h4><q>“${esc(i.hook)}”</q>
      <ol>${i.outline.map((o) => `<li>${esc(o)}</li>`).join("")}</ol>
      <p class="src" style="margin:8px 0 0">${esc(i.why_it_should_work)}</p></div>`).join("");
}

async function runAI(btn, target, fn, render) {
  btn.disabled = true; target.innerHTML = loading();
  try { target.innerHTML = render(await fn()); }
  catch (e) { target.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
  btn.disabled = false;
}

async function renderPostsTab() {
  const body = $("#drawer-body"); body.innerHTML = loading();
  try {
    const posts = await api(`/api/accounts/${encodeURIComponent(state.acct.id)}/posts?window=30d`);
    body.innerHTML = posts.map((p) => `<div class="card post" data-post="${esc(p.id)}">
      <img src="${esc(p.thumbnail_url && p.thumbnail_url.startsWith("http") ? p.thumbnail_url : "/api/thumb/" + p.id)}" alt="" loading="lazy">
      <div><h4>${esc(p.title)}</h4><p class="hook">“${esc(p.hook)}”</p>
        <div class="m"><span>${fmt(p.views["30d"])} views (30d)</span><span>${fmt(p.views["7d"])} (7d)</span><span>♥ ${fmt(p.likes)}</span><span>💬 ${fmt(p.comments)}</span></div></div>
      <div class="full"><button class="btn" data-action="analyze" data-id="${esc(p.id)}">✦ Why did this work?</button><div class="ai-out" style="margin-top:10px"></div></div></div>`).join("") ||
      '<div class="card"><p>No posts available.</p></div>';
  } catch (e) { body.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
}

function insightHtml(i) {
  return `<div class="ai-head"><b>Hook strength ${i.hook_strength}/10</b>${srcBadge(i)}</div>
    <div class="meter">${Array.from({ length: 10 }, (_, n) => `<i class="${n < i.hook_strength ? "f" : ""}"></i>`).join("")}</div>
    <p>${esc(i.hook_reason)}</p>
    <p><b>Pacing:</b> ${esc(i.pacing)}</p><p><b>Thumbnail:</b> ${esc(i.thumbnail_notes)}</p><p><b>Trend fit:</b> ${esc(i.trend_fit)}</p>${list(i.key_takeaways)}`;
}

/* ------------------------------------------------------------ modals */
function openModal(html) { $("#modal-card").innerHTML = html; $("#modal").hidden = false; }
function closeModal() { $("#modal").hidden = true; }

function openAdd() {
  openModal(`<h2>Add account</h2><p class="sub">Connect another YouTube, Instagram or Facebook account. Demo mode: any handle works and data is generated.</p>
    <div class="field"><label>Platform</label><div class="seg" id="add-platform">
      <button data-p="youtube" class="on">YouTube</button><button data-p="instagram">Instagram</button><button data-p="facebook">Facebook</button></div></div>
    <div class="field"><label for="add-handle">Handle or channel URL</label><input type="text" id="add-handle" placeholder="@yourcreator" autocomplete="off"></div>
    <p class="err" id="add-err" hidden></p>
    <div class="row-btns"><button class="btn" data-action="close-modal">Cancel</button><button class="btn primary" data-action="submit-add">Add account</button></div>`);
  $("#add-handle").focus();
}

async function submitAdd() {
  const platform = $("#add-platform .on").dataset.p, handle = $("#add-handle").value.trim(), err = $("#add-err"), btn = $("[data-action=submit-add]");
  err.hidden = true; btn.disabled = true;
  try {
    const acc = await send("/api/accounts", { platform, handle });
    closeModal(); toast(`Added ${acc.display_name}`); loadBoard();
  } catch (e) { err.textContent = e.message; err.hidden = false; }
  btn.disabled = false;
}

function openIdeas() {
  openModal(`<h2>Idea generator</h2><p class="sub">Content ideas across all accounts, based on your top-performing posts.</p><div id="ideas-out">${loading()}</div>
    <div class="row-btns"><button class="btn" data-action="close-modal">Close</button><button class="btn primary" data-action="ideas-again">↻ Regenerate</button></div>`);
  loadIdeasModal();
}
async function loadIdeasModal() {
  const out = $("#ideas-out"); out.innerHTML = loading();
  try { out.innerHTML = ideasHtml(await send("/api/ai/ideas", { account_id: null, count: 5 })); }
  catch (e) { out.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
}

/* ------------------------------------------------------------ events */
document.addEventListener("click", async (e) => {
  const t = e.target;
  const seg = (sel, key, attr) => { const b = t.closest(`${sel} button`); if (!b) return false; state[key] = b.dataset[attr]; $$(`${sel} button`).forEach((x) => x.classList.toggle("on", x === b)); loadBoard(); return true; };
  if (seg("#seg-platform", "platform", "platform") || seg("#seg-window", "window", "window") || seg("#seg-metric", "metric", "metric")) return;

  const rm = t.closest("[data-remove]");
  if (rm) { e.stopPropagation(); try { await api("/api/accounts/" + encodeURIComponent(rm.dataset.remove), { method: "DELETE" }); toast("Account removed"); loadBoard(); } catch (er) { toast(er.message); } return; }

  const row = t.closest("tr.row"); if (row) return openDrawer(row.dataset.id);
  const tab = t.closest("#drawer-tabs button"); if (tab) return setTab(tab.dataset.tab);
  const addp = t.closest("#add-platform button"); if (addp) { $$("#add-platform button").forEach((x) => x.classList.toggle("on", x === addp)); return; }

  const act = t.closest("[data-action]"); if (!act) return;
  switch (act.dataset.action) {
    case "add": return openAdd();
    case "ideas": return openIdeas();
    case "ideas-again": return loadIdeasModal();
    case "close-modal": return closeModal();
    case "close-drawer": return closeDrawer();
    case "submit-add": return submitAdd();
    case "strategy": return runAI(act, $("#ai-strategy"), () => send("/api/ai/channel-strategy", { account_id: state.acct.id }), strategyHtml);
    case "channel-ideas": return runAI(act, $("#ai-ideas"), () => send("/api/ai/ideas", { account_id: state.acct.id, count: 4 }), ideasHtml);
    case "analyze": return runAI(act, act.parentElement.querySelector(".ai-out"), () => send("/api/ai/analyze", { post_id: act.dataset.id }), insightHtml);
  }
});
$("#scrim").addEventListener("click", closeDrawer);
$("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") closeModal(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { if (!$("#modal").hidden) closeModal(); else if (!$("#drawer").hidden) closeDrawer(); }
  if (e.key === "Enter" && e.target.id === "add-handle") submitAdd();
});

loadBoard();
