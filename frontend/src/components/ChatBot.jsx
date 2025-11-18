import { useState, useEffect, useRef } from "react";
import { useAuth, useUser } from "@clerk/clerk-react";
import {
  MessageCircle,
  X,
  Send,
  User,
  Brain,
  Minimize2,
  Maximize2,
} from "lucide-react";

const ChatBot = () => {
  const { userId, isSignedIn } = useAuth();
  const { user } = useUser();

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const CHATBOT_API_URL =
    import.meta.env.VITE_API_URL || "http://localhost:5000";

  // 🔥 CLEAN THE RESPONSE (remove ```json and ``` blocks)
  const cleanAgentResponse = (text) => {
    if (!text) return text;

    return text
      .replace(/```json/gi, "")
      .replace(/```/g, "")
      .replace(/\n/g, " ")
      .trim();
  };

  // ------------------------------------------
  // INITIAL WELCOME MESSAGE
  // ------------------------------------------
  useEffect(() => {
    if (isSignedIn && isOpen && messages.length === 0) {
      const username =
        user?.firstName || user?.fullName || user?.username || "there";

      setMessages([
        {
          type: "bot",
          content: `Hi ${username}! 👋 I'm your ElevateU learning agent. How can I help today?`,
          timestamp: new Date().toISOString(),
          agent: true,
        },
      ]);
    }
  }, [isSignedIn, isOpen, user, messages.length]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // ------------------------------------------
  // SEND MESSAGE → AI AGENT ENDPOINT
  // ------------------------------------------
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const newUserMsg = {
      type: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(`${CHATBOT_API_URL}/api/chatbot/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputMessage,
          userId,
          userName: user?.firstName,
          userEmail: user?.primaryEmailAddress?.emailAddress,
          sessionId: `session_${Date.now()}`,
        }),
      });

      const data = await response.json();

      // ✔ Extract only the reply (NO JSON SHOWN TO USER)
      const cleanedReply = cleanAgentResponse(data.reply);

      const newBotMsg = {
        type: "bot",
        content: cleanedReply || "I'm here to help!",
        action: data.action,
        data: data.data,
        agent: true,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, newBotMsg]);
    } catch (error) {
      console.error("Agent error:", error);

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content:
            "Oops! I had trouble connecting to the server. Please try again.",
          error: true,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // ------------------------------------------
  // ENTER KEY HANDLER
  // ------------------------------------------
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isSignedIn) return null;

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:scale-105 transition z-50"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border overflow-hidden z-50 flex flex-col">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <MessageCircle className="w-6 h-6" />
              <div>
                <h3 className="font-semibold">Learning Assistant</h3>
                <p className="text-xs opacity-80">AI-powered Agent</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:text-white"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4" />
                ) : (
                  <Minimize2 className="w-4 h-4" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4 max-h-[480px]">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${
                      msg.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-3 rounded-xl text-sm ${
                        msg.type === "user"
                          ? "bg-blue-500 text-white"
                          : "bg-white border shadow-sm"
                      }`}
                    >
                      {/* Label */}
                      <div className="flex items-center space-x-2 mb-1">
                        {msg.type === "bot" && (
                          <>
                            <Brain className="w-4 h-4 text-blue-600" />
                            <span className="text-xs text-blue-600 font-medium">
                              AI Agent
                            </span>
                          </>
                        )}
                        {msg.type === "user" && (
                          <>
                            <User className="w-4 h-4 opacity-80" />
                            <span className="text-xs opacity-80">You</span>
                          </>
                        )}
                      </div>

                      {/* Message */}
                      <p className="whitespace-pre-wrap">{msg.content}</p>

                      {/* Timestamp */}
                      <div className="text-[10px] text-gray-400 mt-1">
                        {new Date(msg.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Agent Thinking */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="px-4 py-3 bg-white border rounded-xl shadow-sm flex items-center space-x-2">
                      <Brain className="text-blue-600 animate-pulse w-4 h-4" />
                      <span className="text-gray-600 text-sm">Thinking...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-3 border-t bg-white flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask something..."
                  className="flex-1 px-3 py-2 rounded-xl border text-sm focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-blue-500 text-white p-3 rounded-xl hover:bg-blue-600 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default ChatBot;