
import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load conversation history from PostgreSQL through FastAPI
  const loadHistory = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/conversations"
      );

      const data = await response.json();

      setHistory(data.conversations);
    } catch (error) {
      console.error("Unable to load conversation history:", error);
    }
  };

  // Load history when the application starts
  useEffect(() => {
    loadHistory();
  }, []);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const userQuestion = question;

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
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });

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

      // Refresh history after every new conversation
      loadHistory();

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: "Unable to connect to the backend.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="app">

      <div className="header">
        <h1>Enterprise Knowledge Platform</h1>
        <p>HR • IT • Company Policies</p>
      </div>

      <div className="history-container">
        <h2>Conversation History</h2>

        {history.length === 0 ? (
          <p>No conversations yet.</p>
        ) : (
          history.map((conversation) => (
            <div
              key={conversation.id}
              className="history-item"
            >
              <strong>{conversation.question}</strong>

              <p>{conversation.answer}</p>

              <div className="metadata">
                <span>
                  Agent: {conversation.agent}
                </span>

                <span>
                  Source:{" "}
                  {conversation.sources?.length > 0
                    ? conversation.sources.join(", ")
                    : "None"}
                </span>

                {conversation.escalated && (
                  <span>⚠️ Escalated</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="chat-container">

        {messages.length === 0 && (
          <div className="welcome">
            <h2>How can I help you?</h2>
            <p>
              Ask questions about HR, IT support, or company policies.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={
              message.type === "user"
                ? "message user-message"
                : "message assistant-message"
            }
          >
            <strong>
              {message.type === "user"
                ? "You"
                : "Assistant"}
            </strong>

            <p>{message.text}</p>

            {message.type === "assistant" &&
              message.agent && (
                <div className="metadata">

                  <span>
                    Agent: {message.agent}
                  </span>

                  <span>
                    Retrieval score: {message.confidence}
                  </span>

                  {message.sources?.length > 0 && (
                    <span>
                      Source:{" "}
                      {message.sources.join(", ")}
                    </span>
                  )}

                  {message.escalated && (
                    <span>
                      ⚠️ Escalated for review
                    </span>
                  )}

                </div>
              )}
          </div>
        ))}

        {loading && (
          <div className="message assistant-message">
            <strong>Assistant</strong>
            <p>Thinking...</p>
          </div>
        )}

      </div>

      <div className="input-area">

        <input
          type="text"
          placeholder="Ask a question..."
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

        <button onClick={sendQuestion}>
          Send
        </button>

      </div>

    </div>
  );
}

export default App;

