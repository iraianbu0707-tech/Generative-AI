const contentbar = document.getElementById("content-type");
const but = document.getElementById("send-button");
const inputbar = document.getElementById("user-input");
const output = document.getElementById("chat-window");
 
but.addEventListener("click", async function (event) {
  const selectedcontent = contentbar.value;
  const topic = inputbar.value.trim();
 
  if (!topic) return;
 
  const userBubble = document.createElement("div");
  userBubble.classList.add("message", "user");
  userBubble.textContent = topic;
  output.appendChild(userBubble);
 
  inputbar.value = "";
 
  // Show a loading bubble on the left while waiting for Gemini
  const bubble = document.createElement("div");
  bubble.classList.add("message", "loading");
  bubble.textContent = "Generating ...";
  output.appendChild(bubble);
 
  output.scrollTop = output.scrollHeight;
 
  try {
    const response = await fetch("http://127.0.0.1:5000/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ "topic": topic, "content_type": selectedcontent })
    });
 
    const data = await response.json();
 
    const reply = document.createElement("div");
    reply.classList.add("message", "bot");
    reply.textContent = data.reply;
 
    bubble.remove();
    output.appendChild(reply);
 
  } catch (error) {
    bubble.remove();
    console.log("error:", error);
  }
 
  output.scrollTop = output.scrollHeight;
});
 
// ---------- History panel ----------
 
const historyButton = document.getElementById("history-button");
const historyPanel = document.getElementById("history-panel");
 
historyButton.addEventListener("click", async function () {
  historyPanel.classList.toggle("hidden");
 
  try {
    const response = await fetch("http://127.0.0.1:5000/history");
    const data = await response.json();
 
    historyPanel.innerHTML = "";
 
    for (const item of data) {
      const entry = document.createElement("div");
      entry.classList.add("history-item");
      entry.innerHTML = `
        <div class="history-meta">${item.content_type}</div>
        <div class="history-topic">${item.topic}</div>
        <div class="history-output">${item.output}</div>
      `;
      historyPanel.appendChild(entry);
    }
 
  } catch (error) {
    console.log("Error:", error);
  }
});