"use client"

import { ArrowLeft, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

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

export default function ChatbotPage() {
  return (
    <div className="flex flex-col min-h-screen bg-black">
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            <span className="bg-gradient-to-r from-[#FF5C41] via-[#F39C12] via-[#E67E22] via-[#BB8FCE] to-[#9B59B6] text-transparent bg-clip-text">Nebula</span>
          </h1>
          <p className="text-gray-400">Your AI-powered cosmic companion for machine learning</p>
          <div className="h-1 w-32 bg-gradient-to-r from-[#A277FF] via-[#E056FD] to-[#6153CC] rounded-full mt-4 mx-auto shadow-[0_0_15px_5px_rgba(162,119,255,0.3)]"></div>
        </div>
        <Chatbot />
      </main>
    </div>
  )
}

function Chatbot() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Welcome to Nebula! I'm your cosmic AI assistant. How can I help you with machine learning today?" },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message
    const userMessage = { role: "user", content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Compile conversation history
    const conversationHistory = messages.map((msg) => `${msg.role}: ${msg.content}`).join("\n")

    try {
      // Send request to Flask backend
      const response = await fetch("http://localhost:5001/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          history: conversationHistory,
        }),
      })

      if (!response.ok) {
        throw new Error("Network response was not ok")
      }

      const data = await response.json()

      // Add assistant message
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }])
    } catch (error) {
      console.error("Error:", error)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error processing your request. Please try again later.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([
      { role: "assistant", content: "Chat cleared. How can I help you with Nebula today?" },
    ])
  }

  const router = useRouter()

  const handleBack = () => {
    router.push("/main")
  }

  return (
    <div className="flex flex-col h-[70vh] bg-black rounded-lg shadow-[0_0_30px_rgba(162,119,255,0.2)] overflow-hidden border border-[#3A005A] relative">
      {/* Nebula stars effect */}
      <StarsEffect />
      
      {/* Glowing border effect */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 border border-[#A277FF] rounded-lg opacity-50 blur-[2px]"></div>
      </div>
      
      {/* Header with Back and Clear Buttons */}
      <div className="bg-black border-b border-[#3A005A] p-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <button 
            onClick={handleBack}
            className="flex items-center bg-[#3A005A] hover:bg-[#4C0066] text-[#A277FF] px-3 py-1.5 rounded-md transition-colors duration-200 text-sm"
          >
            <ArrowLeft size={16} className="mr-1.5" />
            Back
          </button>
          
          <div className="flex items-center">
            <div className="w-3 h-3 bg-[#A277FF] rounded-full mr-2 shadow-[0_0_10px_rgba(162,119,255,0.7)]"></div>
            <span className="text-[#A277FF] font-medium">Nebula Active</span>
          </div>
        </div>
        
        <button 
          onClick={clearChat}
          className="flex items-center bg-[#3A005A] hover:bg-[#4C0066] text-[#A277FF] px-3 py-1.5 rounded-md transition-colors duration-200 text-sm"
        >
          <Trash2 size={16} className="mr-1.5" />
          Clear Chat
        </button>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-black bg-[radial-gradient(#A277FF08_1px,transparent_1px)] [background-size:16px_16px]">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-3 ml-2">
            <div className="flex space-x-1">
              <div className="w-2.5 h-2.5 bg-[#A277FF] rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
              <div
                className="w-2.5 h-2.5 bg-[#E056FD] rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              ></div>
              <div
                className="w-2.5 h-2.5 bg-[#6153CC] rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              ></div>
            </div>
            <span className="text-sm text-[#A277FF]">Nebula is processing...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="border-t border-[#3A005A] p-4 bg-black">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Nebula anything..."
            className="flex-1 rounded-full border border-[#3A005A] bg-black/60 px-4 py-3 text-white focus:outline-none focus:border-[#A277FF] focus:ring-1 focus:ring-[#A277FF] transition-all duration-200"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-[#A277FF] to-[#6153CC] text-white rounded-full w-12 h-12 flex items-center justify-center hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[#A277FF] focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-[0_0_15px_rgba(162,119,255,0.5)]"
          >
            <SendIcon />
          </button>
        </form>
      </div>
      
      <style jsx global>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  )
}

function ChatMessage({ message }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
        max-w-[80%] rounded-2xl px-5 py-3 shadow-lg
        ${isUser 
          ? "bg-black text-white rounded-br-none border border-[#A277FF]" 
          : "bg-black text-white rounded-bl-none border border-[#3A005A]"
        }
      `}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  )
}

function SendIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
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
  )
}