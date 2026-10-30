/**
 * Serverless Study Assistant - Frontend Client
 * Student: Dhanush S (23MIS0224) | VIT | Agile Development Process & DevOps
 * Faculty: Prof. Arun Kumar
 */

// Base API configuration (falls back to local backend origin)
const API_BASE_URL = window.location.port === "8000" 
  ? "" 
  : (window.FRONTEND_API_BASE_URL || "http://127.0.0.1:8000");

// DOM elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const charCounter = document.getElementById("char-counter");
const statusPill = document.getElementById("system-status");
const modelVersionTag = document.getElementById("model-version-tag");
const engineDisplay = document.getElementById("engine-display");
const storageDisplay = document.getElementById("storage-display");
const btnClear = document.getElementById("btn-clear");
const btnRetrain = document.getElementById("btn-retrain");
const promptChips = document.querySelectorAll(".prompt-chip");

let currentConversationId = "conv-" + Math.random().toString(36).substring(2, 10);

// Initialize system status
async function checkSystemHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();
    
    statusPill.innerHTML = `
      <span class="status-dot"></span>
      <span class="status-label">Online (${data.environment})</span>
    `;
    modelVersionTag.textContent = `Version: ${data.app_version}`;
    engineDisplay.textContent = data.ai_provider;
    storageDisplay.textContent = data.storage_mode;
  } catch (err) {
    statusPill.innerHTML = `
      <span class="status-dot" style="background:#f43f5e; box-shadow:0 0 8px #f43f5e;"></span>
      <span class="status-label" style="color:#f43f5e;">Backend Offline</span>
    `;
    console.warn("Backend unavailable:", err.message);
  }
}

// Fetch active model version
async function fetchModelVersion() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/model-version`);
    if (res.ok) {
      const data = await res.json();
      modelVersionTag.textContent = data.record_version;
    }
  } catch (e) {
    // Silent fail
  }
}

// Append a message bubble to chat
function appendMessage(sender, text, meta = {}) {
  const row = document.createElement("div");
  row.className = `message-row ${sender}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = sender === "user" ? "ME" : "AI";

  const content = document.createElement("div");
  content.className = "message-content";

  const header = document.createElement("div");
  header.className = "message-header";

  const name = document.createElement("span");
  name.className = "sender-name";
  name.textContent = sender === "user" ? "Dhanush S (Student)" : "Study Assistant";
  header.appendChild(name);

  if (meta.response_mode) {
    const badge = document.createElement("span");
    badge.className = `badge ${meta.response_mode}`;
    badge.textContent = meta.response_mode === "ai" ? "Groq (LLaMA)" : "Rule-Based Fallback";
    header.appendChild(badge);
  }

  const textDiv = document.createElement("div");
  textDiv.className = "message-text";
  
  // Format simple markdown headers and line breaks
  const formatted = text
    .replace(/^### (.*$)/gim, '<h4 style="color:#38bdf8; margin: 8px 0 4px 0;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
  textDiv.innerHTML = formatted;

  content.appendChild(header);
  content.appendChild(textDiv);

  if (meta.duration_ms !== undefined) {
    const footer = document.createElement("div");
    footer.className = "meta-footer";
    footer.innerHTML = `
      <span>Latency: ${meta.duration_ms}ms</span>
      <span>Model: ${meta.model_identifier || "heuristic-v1"}</span>
      <span>Stored: ${meta.storage_recorded ? "Recorded" : "Local-only"}</span>
    `;
    content.appendChild(footer);
  }

  row.appendChild(avatar);
  row.appendChild(content);
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return row;
}

// Append loading indicator
function appendTypingIndicator() {
  const row = document.createElement("div");
  row.className = "message-row assistant typing-row";
  row.id = "typing-indicator";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "AI";

  const content = document.createElement("div");
  content.className = "message-content";
  content.innerHTML = `
    <div class="typing-dots">
      <span></span><span></span><span></span>
    </div>
  `;

  row.appendChild(avatar);
  row.appendChild(content);
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
  const elem = document.getElementById("typing-indicator");
  if (elem) elem.remove();
}

// Send message to FastAPI backend
async function handleSendMessage(messageText) {
  const text = (messageText || userInput.value).trim();
  if (!text) return;

  appendMessage("user", text);
  userInput.value = "";
  charCounter.textContent = "0 / 2000";
  sendButton.disabled = true;

  appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        conversation_id: currentConversationId
      })
    });

    removeTypingIndicator();

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      appendMessage("assistant", `Error: ${errData.message || "Failed to receive response from backend."}`);
      return;
    }

    const data = await res.json();
    appendMessage("assistant", data.reply, {
      response_mode: data.response_mode,
      duration_ms: data.duration_ms,
      model_identifier: data.model_identifier,
      storage_recorded: data.storage_recorded
    });

  } catch (err) {
    removeTypingIndicator();
    appendMessage("assistant", `Network Connection Error: Could not reach the API at ${API_BASE_URL}. Ensure uvicorn backend is running.`);
  } finally {
    sendButton.disabled = false;
    userInput.focus();
  }
}

// Form submit handler
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  handleSendMessage();
});

// Enter key submit, Shift+Enter for newline
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSendMessage();
  }
});

// Character counter
userInput.addEventListener("input", () => {
  const len = userInput.value.length;
  charCounter.textContent = `${len} / 2000`;
  if (len > 2000) {
    charCounter.style.color = "#f43f5e";
  } else {
    charCounter.style.color = "var(--text-secondary)";
  }
});

// Example prompts click
promptChips.forEach(chip => {
  chip.addEventListener("click", () => {
    const query = chip.getAttribute("data-query");
    if (query) {
      handleSendMessage(query);
    }
  });
});

// Clear chat
btnClear.addEventListener("click", () => {
  chatMessages.innerHTML = "";
  currentConversationId = "conv-" + Math.random().toString(36).substring(2, 10);
  appendMessage("assistant", "Chat session cleared. Ready for your next study questions!");
});

// Trigger MLOps Retrain Run
btnRetrain.addEventListener("click", async () => {
  btnRetrain.disabled = true;
  btnRetrain.textContent = "Running MLOps Retraining...";
  appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE_URL}/api/mlops/retrain-simulation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trigger_reason: "Interactive faculty demonstration trigger"
      })
    });

    removeTypingIndicator();

    if (res.ok) {
      const data = await res.json();
      modelVersionTag.textContent = data.new_version;
      const metrics = data.metrics;
      const reportMsg = (
        `### [MLOps Pipeline Execution Report: ${data.run_id}]\n\n` +
        `**Status:** ${data.status.toUpperCase()}\n` +
        `**Model Version Transition:** \`${data.previous_version}\` -> \`${data.new_version}\`\n` +
        `**Benchmark Samples Evaluated:** ${data.dataset_samples_evaluated}\n\n` +
        `**Automated Evaluation Metrics:**\n` +
        `- Benchmark Accuracy: **${(metrics.benchmark_accuracy * 100).toFixed(1)}%**\n` +
        `- Average Precision: **${metrics.average_precision.toFixed(3)}**\n` +
        `- Average Recall: **${metrics.average_recall.toFixed(3)}**\n` +
        `- Average F1-Score: **${metrics.average_f1_score.toFixed(3)}**\n\n` +
        `**Delivery Automation Status:**\n` +
        `- Local Report Artifact: \`${data.artifact_report_path}\`\n` +
        `- Amazon S3 Cloud Upload: ${data.s3_uploaded ? 'Uploaded to s3://' + data.s3_bucket : 'Disabled (Local File Storage)'}\n` +
        `- DynamoDB Metadata Logging: ${data.dynamodb_recorded ? 'Recorded' : 'SQLite Local Mode'}\n\n` +
        `*Educational note: Successfully simulated CI/CD/CT automated evaluation pipeline for academic study assistant.*`
      );
      appendMessage("assistant", reportMsg, { response_mode: "fallback" });
    } else {
      appendMessage("assistant", "MLOps simulation failed. Please inspect backend logs.");
    }
  } catch (err) {
    removeTypingIndicator();
    appendMessage("assistant", `MLOps simulation trigger error: ${err.message}`);
  } finally {
    btnRetrain.disabled = false;
    btnRetrain.textContent = "Trigger MLOps Retrain Run";
  }
});

// Run initial checks on load
checkSystemHealth();
fetchModelVersion();
