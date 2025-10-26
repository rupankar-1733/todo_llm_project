import React, { useState } from "react";

const suggestions = [
  "Add a high priority task to buy groceries tomorrow",
  "What work tasks are due this week?",
  "Mark 'call mom' as done",
  "Delete my 'gym' task"
];

function isFallbackMessage(text) {
  // Detects when AI replied with a fallback (can adjust phrase as needed)
  if (!text) return false;
  const fallbackPhrases = [
    "only for todo tasks",
    "prompt examples",
    "you can ask me to"
  ];
  return fallbackPhrases.some((phrase) => text.toLowerCase().includes(phrase));
}

function Chat({ onSend }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);

    setMessages((msgs) => [
      ...msgs,
      { sender: "user", text: input }
    ]);
    setInput("");

    const reply = await onSend(input);

    setMessages((msgs) => [
      ...msgs,
      { sender: "user", text: input },
      { sender: "bot", text: reply }
    ]);
    setLoading(false);
  };

  const handleSuggestion = (text) => {
    setInput(text);
  };

  const showSuggestions = () => {
    // Show suggestions if chat is empty or latest AI reply is fallback
    if (messages.length === 0) return true;
    const lastBotMsg = [...messages].reverse().find((m) => m.sender === "bot");
    return lastBotMsg && isFallbackMessage(lastBotMsg.text);
  };

  return (
    <div style={{ maxWidth: 400, margin: "0 auto" }}>
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          minHeight: 300,
          padding: 8,
          marginBottom: 8,
          background: "#fff"
        }}
      >
        {messages.map((msg, i) => (
          <div key={i} style={{ textAlign: msg.sender === "user" ? "right" : "left", margin: "4px 0" }}>
            <b>{msg.sender === "user" ? "You" : "AI"}:</b> {msg.text}
          </div>
        ))}

        {showSuggestions() && (
          <div
            style={{
              background: "#f0f4f8",
              borderRadius: 6,
              padding: "14px 12px",
              marginTop: 12,
              color: "#333",
              fontSize: 14
            }}
          >
            Prompt suggestions:
            <ul style={{ margin: "6px 0 0 20px", padding: 0 }}>
              {suggestions.map((s, idx) => (
                <li
                  key={idx}
                  style={{ cursor: "pointer", margin: "5px 0", color: "#5f3dc4" }}
                  onClick={() => handleSuggestion(s)}
                >
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <form onSubmit={handleSend} style={{ display: "flex", gap: 6 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command..."
          style={{ flex: 1, padding: 6, borderRadius: 6, border: "1px solid #bbb" }}
          disabled={loading}
        />
        <button
          type="submit"
          style={{
            width: 70,
            padding: 6,
            marginLeft: 2,
            background: "#8b5cf6",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: loading ? "not-allowed" : "pointer"
          }}
          disabled={loading}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chat;
