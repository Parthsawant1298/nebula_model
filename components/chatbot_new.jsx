"use client"

import { MessageSquare, X, Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import Draggable from "react-draggable";

// Client-side only stars effect component
function StarsEffect() {
  const [stars, setStars] = useState([]);
  
  useEffect(() => {
    // Generate stars only on the client side
    const newStars = Array.from({ length: 50 }).map((_, i) => ({
      id: i,
      width: Math.random() * 3 + 1,
      height: Math.random() * 3 + 1,
      top: Math.random() * 100,
      left: Math.random() * 100,
      glow: Math.random() * 10 + 5,
      duration: Math.random() * 5 + 3
    }));
    setStars(newStars);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
      {stars.map((star) => (
        <div 
          key={star.id}
          className="absolute rounded-full bg-white" 
          style={{
            width: `${star.width}px`,
            height: `${star.height}px`,
            top: `${star.top}%`,
            left: `${star.left}%`,
            boxShadow: `0 0 ${star.glow}px rgba(255,255,255,0.8)`,
            animation: `twinkle ${star.duration}s infinite ease-in-out`
          }}
        />
      ))}
    </div>
  );
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Welcome to Nebula! I'm your cosmic AI assistant. How can I help you with machine learning today?" },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const nodeRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const GOOGLE_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_API_KEY
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Format conversation history for Gemini
    const formattedHistory = messages.map(msg => ({
      role: msg.role === "assistant" ? "model" : "user",
      parts: [{ text: msg.content }]
    }));

    try {
      // Send request to Gemini API with the provided API key
      const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": GOOGLE_API_KEY
        },
        body: JSON.stringify({
          contents: [
            ...formattedHistory,
            {
              role: "user",
              parts: [{ 
                text: `${input}\n\nRemember you are an AI assistant for Nebula, an automated ML platform that helps users with:\n- Classification, image classification, and object detection models\n- Processing data from uploads, Kaggle datasets, or generating synthetic data\n- Providing visualizations and model performance metrics\n- Exporting trained models with loading code for easy deployment`
              }]
            }
          ],
          generationConfig: {
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 1024,
          }
        }),
      });

      if (!response.ok) {
        throw new Error("API response was not ok");
      }

      const data = await response.json();
      const generatedText = data.candidates[0].content.parts[0].text;

      // Add assistant message
      setMessages((prev) => [...prev, { role: "assistant", content: generatedText }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the AI service. Please try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      { role: "assistant", content: "Chat cleared. I'm here to help with your ML project - from data upload to model training, visualization, and deployment. What would you like to work on?" },
    ]);
  };

  return (
    <Draggable nodeRef={nodeRef} bounds="body" handle=".drag-handle">
      <div 
        ref={nodeRef} 
        className={`fixed z-50 ${isOpen ? 'bottom-6 right-6' : 'bottom-6 right-6'}`}
      >
        {/* Collapsed chat button */}
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            className="w-14 h-14 rounded-full bg-black text-[#A277FF] flex items-center justify-center shadow-[0_0_15px_rgba(162,119,255,0.5)] hover:shadow-[0_0_20px_rgba(162,119,255,0.7)] transition-all duration-300 hover:scale-105 relative border border-[#A277FF]"
            aria-label="Open chat"
          >
            <MessageSquare size={22} />
            <div className="absolute top-0 right-0 w-3 h-3 bg-[#A277FF] rounded-full border-2 border-black"></div>
          </button>
        )}

        {/* Expanded chat window */}
        {isOpen && (
          <div className="flex flex-col w-80 sm:w-96 h-[500px] bg-black rounded-lg shadow-[0_0_30px_rgba(162,119,255,0.2)] overflow-hidden border border-[#3A005A] relative">
            {/* Nebula stars effect */}
            <StarsEffect />
            
            {/* Glowing border effect */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute inset-0 border border-[#A277FF] rounded-lg opacity-50 blur-[2px]"></div>
            </div>
            
            {/* Header */}
            <div className="bg-black border-b border-[#3A005A] p-3 flex justify-between items-center drag-handle cursor-move relative z-10">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-[#A277FF] rounded-full mr-2 shadow-[0_0_10px_rgba(162,119,255,0.7)]"></div>
                <h3 className="text-[#A277FF] font-medium text-sm">Nebula AI Assistant</h3>
              </div>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={clearChat}
                  className="text-[#A277FF] hover:text-white p-1 rounded transition"
                  aria-label="Clear chat"
                >
                  <Trash2 size={16} />
                </button>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-[#A277FF] hover:text-white p-1 rounded transition"
                  aria-label="Close chat"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-black bg-[radial-gradient(#A277FF08_1px,transparent_1px)] [background-size:16px_16px]">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center space-x-3 ml-2">
                  <div className="flex space-x-1">
                    <div className="w-2.5 h-2.5 bg-[#A277FF] rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                    <div className="w-2.5 h-2.5 bg-[#E056FD] rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                    <div className="w-2.5 h-2.5 bg-[#6153CC] rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                  </div>
                  <span className="text-sm text-[#A277FF]">Nebula is processing...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-[#3A005A] p-3 bg-black">
              <form onSubmit={handleSubmit} className="flex space-x-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Nebula anything..."
                  className="flex-1 rounded-full border border-[#3A005A] bg-black/60 px-4 py-2.5 text-white focus:outline-none focus:border-[#A277FF] focus:ring-1 focus:ring-[#A277FF] transition-all duration-200"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="bg-gradient-to-r from-[#A277FF] to-[#6153CC] text-white rounded-full w-10 h-10 flex items-center justify-center hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[#A277FF] focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-[0_0_15px_rgba(162,119,255,0.5)]"
                >
                  <SendIcon />
                </button>
              </form>
            </div>
          </div>
        )}
        <style jsx global>{`
          @keyframes twinkle {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
          }
        `}</style>
      </div>
    </Draggable>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[80%] rounded-2xl px-4 py-2.5 shadow-lg
          ${isUser 
            ? "bg-black text-white rounded-br-none border border-[#A277FF]" 
            : "bg-black text-white rounded-bl-none border border-[#3A005A]"
          }
        `}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}

function SendIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="22" y1="2" x2="11" y2="13"></line>
      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
  );
}