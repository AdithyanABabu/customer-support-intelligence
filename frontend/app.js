const $ = (sel) => document.querySelector(sel);
const badgeClass = (level) => String(level).toLowerCase() === "high" ? "high"
  : String(level).toLowerCase() === "medium" ? "medium" : "ok";

const SAMPLES = [
  {
    name: "Phishing / social engineering",
    text: "From: support@paypa1-security.com\n\nDear customer,\n\nYour PayPal account has been suspended due to unusual activity. Verify your account within 24 hours or it will be permanently closed.\n\nClick here to confirm: http://paypa1-verify-example.com\n\nEnter your password and OTP code to restore access. Attached: Invoice_2024_final.exe\n\nAct immediately. Final notice.",
  },
  {
    name: "Angry refund complaint",
    text: "From: angry_customer_77@example.com\nSubject: WHERE IS MY REFUND?\n\nI asked for a refund 3 weeks ago and you have completely ignored me! This is absolutely unacceptable. I was charged twice for my order #ORD-884213 and nobody is responding. I want my money back TODAY or I will cancel my account. You people are useless and unprofessional!",
  },
  {
    name: "Delivery delay (neutral)",
    text: "From: jane.doe@gmail.com\nSubject: Order lookup\n\nHi, I just wanted to check on the status of my order #8874321 - it says it was shipped last week but I haven't received any tracking update. Could you let me know when it should arrive? Thanks for your help.",
  },
];

function showToast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 2600);
}

function setTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  $("#tab-analyze").classList.toggle("hidden", name !== "analyze");
  $("#tab-dashboard").classList.toggle("hidden", name !== "dashboard");
  if (name === "dashboard") refreshDashboard();
}

document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => setTab(t.dataset.tab)));
$("#btn-clear").addEventListener("click", () => { $("#message-input").value = ""; $("#result-card").classList.add("hidden"); });

$("#btn-sample").addEventListener("click", () => {
  const sample = SAMPLES[Math.floor(Math.random() * SAMPLES.length)];
  $("#message-input").value = sample.text;
  showToast(`Sample loaded: ${sample.name}`);
});

$("#btn-analyze").addEventListener("click", async () => {
  const btn = $("#btn-analyze");
  const text = $("#message-input").value.trim();
  if (!text) { showToast("Paste a message first"); return; }
  btn.classList.add("is-loading");
  btn.disabled = true;
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    renderResult(data);
    refreshDashboard();
  } catch (e) {
    showToast("Analysis failed: " + e.message);
  } finally {
    btn.classList.remove("is-loading");
    btn.disabled = false;
  }
});

function renderResult(data) {
  const card = $("#result-card");
  card.classList.remove("hidden");
  if (data.error) {
    $("#risk-badge").textContent = "Error";
    $("#risk-badge").className = "badge high";
    $("#result-body").innerHTML = `<p class="hint">${data.error}</p>`;
    return;
  }

  const risk = data.risk || {};
  const cust = data.customer_intelligence || {};
  const sec = data.security_intelligence || {};
  const badge = $("#risk-badge");
  badge.textContent = risk.level || "-";
  badge.className = "badge " + badgeClass(risk.level);

  const subtopics = data.topic_scores ? "" : "";
  void subtopics;

  const customerBox = `
    <div class="sec">
      <div class="sec-title">Customer intelligence</div>
      <div class="grid-3">
        ${statBox("Topic", esc(cust.topic || "General"))}
        ${statBox("Sentiment", esc(cust.sentiment || "Neutral"), clsForSent(cust.sentiment))}
        ${statBox("Urgency", esc(cust.urgency || "Normal"), cust.urgency === "High" ? "warn" : "good")}
      </div>
      <div class="summary-box mt">${esc(cust.summary || "")}</div>
      ${orderAmounts(cust)}
    </div>
  `;

  const flags = sec.flags || {};
  const flagList = [
    ["suspicious_url", "Suspicious URL"],
    ["malicious_domain", "Suspicious domain"],
    ["impersonation", "Impersonation"],
    ["credential_request", "Credential request"],
    ["payment_request", "Suspicious payment"],
    ["urgency_tactics", "Urgency tactics"],
    ["threat_tactics", "Threat / scare"],
    ["attachment_risk", "Dangerous attachment"],
  ].map(([k, label]) => `<span class="flag ${flags[k] ? "on" : ""}">${label}</span>`).join("");

  const securityBox = `
    <div class="sec">
      <div class="sec-title">Security intelligence</div>
      <div class="grid-3">
        ${statBox("Phishing", sec.phishing_detected ? "Detected" : "Clear", sec.phishing_detected ? "bad" : "good")}
        ${statBox("Social engineering", sec.social_engineering ? "Possible" : "None", sec.social_engineering ? "warn" : "good")}
        ${statBox("Risk score", sec.risk_score ?? 0, clsForScore(sec.risk_score))}
      </div>
      <div class="flag-list">${flagList}</div>
      ${urlList(sec)}
      <ul class="findings">${renderFindings(sec.findings || [])}</ul>
    </div>
  `;

  const actionsBox = `
    <div class="sec">
      <div class="sec-title">Recommended action</div>
      <div class="actions">
        ${(data.recommended_actions || []).map((a) => `<div class="action-item">${esc(a)}</div>`).join("")}
      </div>
    </div>
  `;

  $("#result-body").innerHTML = customerBox + securityBox + actionsBox;
}

function statBox(label, value, cls = "") {
  return `<div class="stat-box"><div class="label">${label}</div><div class="value ${cls}">${value}</div></div>`;
}

function clsForSent(s) {
  if (s === "Angry" || s === "Frustrated") return "bad";
  if (s === "Happy") return "good";
  return "";
}
function clsForScore(score) {
  if ((score ?? 0) >= 8) return "bad";
  if ((score ?? 0) >= 4) return "warn";
  return "good";
}

function orderAmounts(cust) {
  const parts = [];
  if (cust.order_numbers && cust.order_numbers.length) parts.push(`Order(s): ${esc(cust.order_numbers.join(", "))}`);
  if (cust.amounts && cust.amounts.length) parts.push(`Amount(s): ${esc(cust.amounts.join(", "))}`);
  if (!parts.length) return "";
  return `<div class="hint">${parts.join(" &middot; ")}</div>`;
}

function urlList(sec) {
  const urls = sec.suspicious_urls || [];
  if (!urls.length) return "";
  return `<div class="hint mt">Suspicious URLs: ${urls.map((u) => `<code>${esc(u)}</code>`).join("<br>")}</div>`;
}

function renderFindings(findings) {
  return findings.map((f) => {
    const isAlert = /high|impersonat|credential|url|domain|attachment|social/i.test(f);
    return `<li class="${isAlert ? "alert" : ""}">${esc(f)}</li>`;
  }).join("");
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

/* ---------- dashboard ---------- */

async function refreshDashboard() {
  try {
    const res = await fetch("/api/insights?limit=100");
    const data = await res.json();
    const rowsRes = await fetch("/api/messages?limit=25");
    const rows = await rowsRes.json();
    renderStats(data);
    renderBars(data);
    renderInsights(data);
    renderHistory(rows.messages || []);
  } catch (e) {
    showToast("Dashboard load failed: " + e.message);
  }
}

function renderStats(d) {
  const total = d.total || 0;
  const cards = [
    { num: total, lbl: "Messages analyzed", cls: "" },
    { num: d.by_urgency?.High || 0, lbl: "Urgent messages", cls: "urgent" },
    { num: d.phishing_count || 0, lbl: "Phishing detected", cls: d.phishing_count ? "high-risk" : "good" },
    { num: d.by_sentiment?.Happy || 0, lbl: "Happy customers", cls: "good" },
  ];
  $("#stat-cards").innerHTML = cards.map((c) =>
    `<div class="stat-card ${c.cls}"><div class="num">${c.num}</div><div class="lbl">${c.lbl}</div></div>`).join("");
}

function barRow(label, count, total, cls) {
  const pct = total ? Math.round((count / total) * 100) : 0;
  return `<div class="bar-row">
    <div class="bar-top"><span>${esc(label)}</span><span>${count} (${pct}%)</span></div>
    <div class="bar-track"><div class="bar-fill ${cls}" style="width:${pct}%"></div></div>
  </div>`;
}

function renderBars(d) {
  const total = d.total || 0;
  const topics = Object.entries(d.by_topic || {}).sort((a, b) => b[1] - a[1]).slice(0, 8);
  $("#topic-chart").innerHTML = topics.length
    ? topics.map(([k, v]) => barRow(k, v, total, "blue")).join("")
    : emptyNote();

  const sents = ["Happy", "Neutral", "Frustrated", "Angry"];
  $("#sentiment-chart").innerHTML = sents.map((s) =>
    barRow(s, d.by_sentiment?.[s] || 0, total, s === "Angry" || s === "Frustrated" ? "red" : s === "Happy" ? "green" : "blue")).join("");

  const urgency = ["High", "Normal"];
  $("#urgency-chart").innerHTML = urgency.map((u) =>
    barRow(u, d.by_urgency?.[u] || 0, total, u === "High" ? "orange" : "green")).join("");
}

function emptyNote() { return `<p class="empty-note">Analyze a message first to populate charts.</p>`; }

function renderInsights(d) {
  const items = [];
  if (d.repeated_problems?.length) {
    d.repeated_problems.forEach((p) =>
      items.push(insightItem("📈", `${esc(p.insight)} (${p.count} occurrences, ${p.share}% of recent)`)));
  }
  if (d.phishing_count) {
    items.push(insightItem("🛡️", `${d.phishing_count} of the last ${d.total} messages show phishing/social-engineering indicators.`));
  }
  if (d.by_urgency?.High) {
    items.push(insightItem("⚡", `${d.by_urgency.High} messages were marked urgent, suggesting possible response bottlenecks.`));
  }
  const neg = (d.by_sentiment?.Frustrated || 0) + (d.by_sentiment?.Angry || 0);
  if (neg) {
    items.push(insightItem("😤", `${neg} customers expressed frustration or anger — review recent agent responses.`));
  }
  if (!items.length) items.push(insightItem("💡", "No insights yet. Analyze a few messages to detect patterns."));
  $("#insight-list").innerHTML = items.join("");
}

function insightItem(ic, html) {
  return `<div class="insight-item"><span class="ic">${ic}</span><span>${html}</span></div>`;
}

function renderHistory(msgs) {
  const tbody = $("#history-table tbody");
  const empty = $("#history-empty");
  if (!msgs.length) {
    tbody.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");
  tbody.innerHTML = msgs.map((m) => `
    <tr>
      <td>${esc(m.created_at)}</td>
      <td>${esc(m.topic)}</td>
      <td><span class="tag ${m.sentiment === "Happy" ? "good" : m.sentiment === "Neutral" ? "" : "bad"}">${esc(m.sentiment)}</span></td>
      <td><span class="tag ${m.urgency === "High" ? "warn" : "good"}">${esc(m.urgency)}</span></td>
      <td>${m.phishing_detected ? '<span class="tag bad">Yes</span>' : '<span class="tag good">No</span>'}</td>
      <td><span class="tag ${m.risk_level === "HIGH" ? "bad" : m.risk_level === "MEDIUM" ? "warn" : "good"}">${esc(m.risk_level)}</span></td>
    </tr>`).join("");
}

refreshDashboard();