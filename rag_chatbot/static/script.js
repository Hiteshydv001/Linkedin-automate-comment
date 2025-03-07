async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (!userInput) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div><b>You:</b> ${userInput}</div>`;

    document.getElementById("user-input").value = ""; // Clear input

    try {
        const response = await fetch("/rag_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: userInput }),
        });

        const data = await response.json();
        chatBox.innerHTML += `<div><b>Bot:</b> ${data.response}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    } catch (error) {
        console.error("Error:", error);
        chatBox.innerHTML += `<div><b>Bot:</b> Error fetching response.</div>`;
    }
}
