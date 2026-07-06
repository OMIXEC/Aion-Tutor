/**
 * app.js for Aion Tutor Debug Lite
 */
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

const userId = "debug-user";
const sessionId = "debug-" + Math.random().toString(36).substring(7);
let websocket = null;
let is_audio = false;

const enableProactivityCheckbox = document.getElementById("enableProactivity");
const enableAffectiveDialogCheckbox = document.getElementById("enableAffectiveDialog");

function handleRunConfigChange() {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.close();
  }
}

enableProactivityCheckbox.addEventListener("change", handleRunConfigChange);
enableAffectiveDialogCheckbox.addEventListener("change", handleRunConfigChange);

function getWebSocketUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const baseUrl = `${protocol}//${window.location.host}/ws/session/${userId}/${sessionId}`;
  const params = new URLSearchParams();
  if (enableProactivityCheckbox.checked) params.append("proactivity", "true");
  if (enableAffectiveDialogCheckbox.checked) params.append("affective_dialog", "true");
  const qs = params.toString();
  return qs ? `${baseUrl}?${qs}` : baseUrl;
}

const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const statusIndicator = document.getElementById("statusIndicator");
const statusText = document.getElementById("statusText");
const consoleContent = document.getElementById("consoleContent");
const clearConsoleBtn = document.getElementById("clearConsole");
const showAudioEventsCheckbox = document.getElementById("showAudioEvents");

let currentBubbleElement = null;

function addConsoleEntry(type, content, data = null, emoji = null, author = null, isAudio = false) {
  if (isAudio && !showAudioEventsCheckbox.checked) return;
  const entry = document.createElement("div");
  entry.className = `console-entry ${type}`;
  entry.innerHTML = `
    <div class="console-entry-header">
      <div class="console-entry-left">
        ${emoji ? `<span class="console-entry-emoji">${emoji}</span>` : ""}
        <span class="console-entry-type">${type}</span>
        ${author ? `<span class="console-entry-author" data-author="${author}">${author}</span>` : ""}
      </div>
      <span class="console-entry-timestamp">${new Date().toLocaleTimeString()}</span>
    </div>
    <div class="console-entry-content">${content}</div>
  `;
  if (data) {
    const pre = document.createElement("pre");
    pre.className = "console-entry-json collapsed";
    pre.textContent = JSON.stringify(data, null, 2);
    entry.appendChild(pre);
    entry.onclick = () => pre.classList.toggle("collapsed");
  }
  consoleContent.appendChild(entry);
  consoleContent.scrollTop = consoleContent.scrollHeight;
}

function updateConnectionStatus(connected) {
  statusIndicator.classList.toggle("disconnected", !connected);
  statusText.textContent = connected ? "Connected" : "Disconnected";
}

function createMessageBubble(text, role, agentType = "") {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="bubble">
      ${agentType ? `<div style="font-size:0.7rem; opacity:0.6; margin-bottom:4px;">${agentType}</div>` : ""}
      <p class="bubble-text">${text}</p>
    </div>
  `;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return div;
}

function updateMessageBubble(element, text, isPartial = false) {
  const p = element.querySelector(".bubble-text");
  p.textContent = text;
  if (isPartial) {
    const span = document.createElement("span");
    span.className = "typing-indicator";
    p.appendChild(span);
  }
}

function connectWebsocket() {
  const url = getWebSocketUrl();
  websocket = new WebSocket(url);

  websocket.onopen = () => {
    updateConnectionStatus(true);
    document.getElementById("sendButton").disabled = false;
    addConsoleEntry("incoming", "Connected", { url }, "🔌", "system");
  };

  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Handle Aion Agent Swapping Notifications
    if (data.type === "status" && data.agent) {
        createMessageBubble(`Switching to specialized agent: ${data.agent}`, "system");
        return;
    }

    // Handle Gemini Live Bidi Events
    if (data.serverContent?.modelTurn?.parts) {
        data.serverContent.modelTurn.parts.forEach(part => {
            if (part.text) {
                if (!currentBubbleElement) {
                    currentBubbleElement = createMessageBubble(part.text, "agent", "Aion Orchestrator");
                } else {
                    const currentText = currentBubbleElement.querySelector(".bubble-text").textContent;
                    updateMessageBubble(currentBubbleElement, currentText + part.text, true);
                }
            }
        });
    }

    if (data.turnComplete) {
        if (currentBubbleElement) {
            const p = currentBubbleElement.querySelector(".bubble-text");
            p.textContent = p.textContent.replace("...", "");
        }
        currentBubbleElement = null;
    }

    addConsoleEntry("incoming", "Event Received", data, "📨", "orchestrator");
  };

  websocket.onclose = () => {
    updateConnectionStatus(false);
    setTimeout(connectWebsocket, 3000);
  };
}

messageForm.onsubmit = (e) => {
  e.preventDefault();
  const val = messageInput.value.trim();
  if (val && websocket?.readyState === WebSocket.OPEN) {
    createMessageBubble(val, "user");
    websocket.send(JSON.stringify({ type: "text", text: val }));
    messageInput.value = "";
    addConsoleEntry("outgoing", "Sent text", { text: val }, "💬", "user");
  }
};

const startAudioButton = document.getElementById("startAudioButton");
startAudioButton.onclick = () => {
    startAudioButton.disabled = true;
    startAudioButton.textContent = "Audio Active";
    startAudioPlayerWorklet(); // Need to handle promise properly if needed
    startAudioRecorderWorklet((pcm) => {
        if (websocket?.readyState === WebSocket.OPEN) {
            websocket.send(pcm);
        }
    });
    is_audio = true;
};

connectWebsocket();

// Camera logic truncated for brevity, but same as bidi-demo
function setupCamera() {
    const camBtn = document.getElementById("cameraButton");
    const camModal = document.getElementById("cameraModal");
    const video = document.getElementById("cameraPreview");
    camBtn.onclick = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        camModal.classList.add("show");
    };
    document.getElementById("captureImage").onclick = () => {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth; canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        const base64 = canvas.toDataURL("image/jpeg").split(",")[1];
        websocket.send(JSON.stringify({ type: "image", data: base64 }));
        camModal.classList.remove("show");
        createMessageBubble("[Image Sent]", "user");
    };
}
setupCamera();
