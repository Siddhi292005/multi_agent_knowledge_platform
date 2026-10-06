
import { useEffect, useState } from "react";
import "./App.css";
const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");
function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/conversations`);

      const data = await response.json();
      setHistory(data.conversations);
    } catch (error) {
      console.error("Unable to load conversation history:", error);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const sendQuestion = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: data.answer,
          agent: data.agent,
          confidence: data.confidence,
          sources: data.sources,
          escalated: data.escalated,
        },
      ]);

      loadHistory();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: "Unable to connect to the backend. Please make sure the API server is running.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getAgentLabel = (agent) => {
    const labels = {
      hr: "HR",
      it: "IT Support",
      policy: "Company Policy",
      unknown: "Unassigned",
    };

    return labels[agent] || agent;
  };

  return (
    <div className="app">

      <header className="header">
        <div className="brand">
          <div className="brand-icon">EK</div>

          <div>
            <h1>Enterprise Knowledge</h1>
            <p>AI-powered internal knowledge assistant</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System online
        </div>
      </header>

      <main className="main-layout">

        <aside className="history-panel">
          <div className="panel-heading">
            <div>
              <h2>Conversation History</h2>
              <p>Recent questions</p>
            </div>

            <span className="history-count">
              {history.length}
            </span>
          </div>

          <div className="history-list">

            {history.length === 0 ? (
              <div className="empty-history">
                <div className="empty-icon">💬</div>
                <p>No conversations yet.</p>
              </div>
            ) : (
              history.map((conversation) => (
                <div
                  key={conversation.id}
                  className="history-item"
                >
                  <div className="history-question">
                    {conversation.question}
                  </div>

                  <div className="history-answer">
                    {conversation.answer}
                  </div>

                  <div className="history-meta">

                    <span
                      className={`agent-badge ${conversation.agent}`}
                    >
                      {getAgentLabel(conversation.agent)}
                    </span>

                    {conversation.sources?.length > 0 && (
                      <span className="source-label">
                        {conversation.sources.join(", ")}
                      </span>
                    )}

                    {conversation.escalated && (
                      <span className="escalation-badge">
                        Escalated
                      </span>
                    )}

                  </div>
                </div>
              ))
            )}

          </div>
        </aside>

        <section className="chat-panel">

          <div className="chat-header">
            <h2>Knowledge Assistant</h2>

            <p>
              Ask about HR, IT support, or company policies.
            </p>
          </div>

          <div className="chat-container">

            {messages.length === 0 && (
              <div className="welcome">

                <div className="welcome-icon">
                  ✦
                </div>

                <h2>How can I help?</h2>

                <p>
                  Ask a question and I'll search the relevant
                  company knowledge base.
                </p>

                <div className="suggestions">

                  <button
                    onClick={() =>
                      setQuestion(
                        "How many days of sick leave are employees entitled to?"
                      )
                    }
                  >
                    Sick leave policy
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "How do I connect to the company VPN?"
                      )
                    }
                  >
                    VPN instructions
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What are the standard office working hours?"
                      )
                    }
                  >
                    Office hours
                  </button>

                </div>

              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${
                  message.type === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
              >

                <div className="message-label">
                  {message.type === "user"
                    ? "You"
                    : "Assistant"}
                </div>

                <div className="message-content">
                  <p>{message.text}</p>
                </div>

                {message.type === "assistant" &&
                  message.agent &&
                  !message.error && (
                    <div className="answer-meta">

                      <span
                        className={`agent-badge ${message.agent}`}
                      >
                        {getAgentLabel(message.agent)}
                      </span>

                      <span className="confidence">
                        Retrieval score: {message.confidence}
                      </span>

                      {message.sources?.length > 0 && (
                        <span className="source">
                          Source: {message.sources.join(", ")}
                        </span>
                      )}

                      {message.escalated && (
                        <div className="escalation-warning">
                          ⚠ This question has been escalated for
                          review.
                        </div>
                      )}

                    </div>
                  )}

              </div>
            ))}

            {loading && (
              <div className="message assistant-message">

                <div className="message-label">
                  Assistant
                </div>

                <div className="thinking">

                  <span></span>
                  <span></span>
                  <span></span>

                  <p>
                    Searching the knowledge base...
                  </p>

                </div>

              </div>
            )}

          </div>

          <div className="input-section">

            <div className="input-area">

              <input
                type="text"
                placeholder="Ask a question about company policies..."
                value={question}
                onChange={(e) =>
                  setQuestion(e.target.value)
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    sendQuestion();
                  }
                }}
              />

              <button
                onClick={sendQuestion}
                disabled={
                  loading || !question.trim()
                }
              >
                {loading ? "..." : "Send"}
              </button>

            </div>

            <p className="input-hint">
              Press Enter to send
            </p>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;

