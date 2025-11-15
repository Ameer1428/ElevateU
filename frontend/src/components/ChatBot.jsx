import { useState, useEffect, useRef } from 'react'
import { useAuth, useUser } from '@clerk/clerk-react'
import { MessageCircle, X, Send, User, Brain, TrendingUp, Target, BookOpen, Sparkles, Minimize2, Maximize2 } from 'lucide-react'

const ChatBot = () => {
  const { userId, isSignedIn } = useAuth()
  const { user } = useUser()
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [contextInfo, setContextInfo] = useState({ contextUsed: false })
  const messagesEndRef = useRef(null)

  // Use main backend API (port 5000)
  const CHATBOT_API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000"

  useEffect(() => {
    if (isSignedIn && isOpen && messages.length === 0) {
      const userName = user?.firstName || user?.fullName || 'there'
      setMessages([{
        type: 'bot',
        content: `Hi ${userName}! 👋 I'm your AI learning assistant! I can track your progress, recommend courses, and help you study better. What would you like to know?`,
        timestamp: new Date().toISOString(),
        response_type: 'greeting'
      }])
    }
  }, [isSignedIn, isOpen, user, messages.length])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch(`${CHATBOT_API_URL}/api/chatbot/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          userId: userId,
          userName: user?.firstName || user?.fullName || 'User',
          userEmail: user?.primaryEmailAddress?.emailAddress || '',
          sessionId: `session_${Date.now()}`
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      const botMessage = {
        type: 'bot',
        content: data.response,
        timestamp: new Date().toISOString(),
        response_type: data.response_type || 'general',
        suggested_actions: data.suggested_actions || [],
        context_used: data.context_used || false,
        fallback_mode: data.fallback_mode || false,
        agent_used: data.agent_used || false
      }

      setMessages(prev => [...prev, botMessage])
      setContextInfo({
        contextUsed: data.context_used || false
      })

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        type: 'bot',
        content: 'I apologize, but I encountered an error. Please make sure the backend server is running and try again.',
        timestamp: new Date().toISOString(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getResponseIcon = (responseType) => {
    const iconMap = {
      'progress_check': TrendingUp,
      'recommendation': Target,
      'learning_help': BookOpen,
      'motivation': Sparkles,
      'greeting': Brain,
      'provide_guidance': BookOpen,
      'study_tips': Sparkles,
      'general': Sparkles
    }
    const IconComponent = iconMap[responseType] || Sparkles
    return <IconComponent size={14} className="inline mr-1" />
  }

  const getResponseColor = (responseType) => {
    const colorMap = {
      'progress_check': 'text-blue-600',
      'recommendation': 'text-green-600',
      'learning_help': 'text-purple-600',
      'motivation': 'text-yellow-600',
      'greeting': 'text-indigo-600',
      'provide_guidance': 'text-purple-600',
      'study_tips': 'text-yellow-600',
      'general': 'text-gray-600'
    }
    return colorMap[responseType] || 'text-gray-600'
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!isSignedIn) {
    return null
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 z-50 group"
        >
          <MessageCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 bg-gray-800 text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            AI Learning Assistant
          </span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden z-50 flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <MessageCircle className="w-6 h-6" />
                <Brain className="w-2 h-2 absolute -top-0.5 -right-0.5 animate-pulse" />
              </div>
              <div>
                <h3 className="font-semibold">Learning Assistant</h3>
                <p className="text-xs opacity-90">AI-powered guidance</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-white/80 hover:text-white transition-colors p-1"
              >
                {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Context Indicator */}
              {contextInfo.contextUsed && (
                <div className="bg-green-50 border-b border-green-100 px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <p className="text-xs text-green-700 font-medium">
                      🧠 Context-aware - I know your progress
                    </p>
                  </div>
                </div>
              )}

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 messages-area overflow-scroll" style={{
                scrollbarWidth: 'thin',
                scrollbarColor: '#cbd5e1 #f1f5f9',
                scrollBehavior: 'smooth',
                maxHeight: 'calc(600px - 180px)', // Account for header and input area
                minHeight: '0'
              }}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-xl px-4 py-3 ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white ml-auto'
                          : message.error
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                      }`}
                    >
                      {/* Message Header */}
                      <div className="flex items-center space-x-2 mb-2">
                        {message.type === 'bot' && (
                          <>
                            <Brain className={`w-4 h-4 ${getResponseColor(message.response_type)}`} />
                            <span className={`text-xs font-medium ${getResponseColor(message.response_type)}`}>
                              AI Assistant
                            </span>
                            {message.agent_used && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                                🤖 Smart Agent
                              </span>
                            )}
                            {message.response_type && (
                              <span className={`text-xs px-2 py-0.5 rounded-full bg-gray-100 ${getResponseColor(message.response_type)}`}>
                                {getResponseIcon(message.response_type)}
                                {message.response_type.replace('_', ' ').charAt(0).toUpperCase() + message.response_type.replace('_', ' ').slice(1)}
                              </span>
                            )}
                          </>
                        )}
                        {message.type === 'user' && (
                          <>
                            <User className="w-4 h-4 text-white/80" />
                            <span className="text-xs text-white/80 font-medium">You</span>
                          </>
                        )}
                      </div>

                      {/* Message Content */}
                      <div className="text-sm whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </div>

                      {/* Suggested Actions */}
                      {message.suggested_actions && message.suggested_actions.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="flex flex-wrap gap-1.5">
                            {message.suggested_actions.map((action, i) => (
                              <button
                                key={i}
                                onClick={() => setInputMessage(action)}
                                className="text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-colors border border-blue-200 font-medium"
                              >
                                {action}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Timestamp */}
                      <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-white/60' : 'text-gray-400'}`}>
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                      <div className="flex items-center space-x-2">
                        <Brain className="w-4 h-4 text-blue-600 animate-pulse" />
                        <div className="flex space-x-1">
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <span className="text-sm text-gray-600">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Actions */}
              <div className="bg-white border-t border-gray-100 p-3">
                <div className="flex gap-2 mb-3">
                  <button
                    onClick={() => setInputMessage("How am I doing?")}
                    className="flex-1 text-xs bg-blue-50 text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-100 transition-colors font-medium border border-blue-200"
                  >
                    📊 My Progress
                  </button>
                  <button
                    onClick={() => setInputMessage("Recommend courses for me")}
                    className="flex-1 text-xs bg-green-50 text-green-700 px-3 py-2 rounded-lg hover:bg-green-100 transition-colors font-medium border border-green-200"
                  >
                    🎯 Find Courses
                  </button>
                  <button
                    onClick={() => setInputMessage("I need study motivation")}
                    className="flex-1 text-xs bg-purple-50 text-purple-700 px-3 py-2 rounded-lg hover:bg-purple-100 transition-colors font-medium border border-purple-200"
                  >
                    💡 Motivate Me
                  </button>
                </div>

                {/* Input Area */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your question here..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-blue-500 text-white p-3 rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}

export default ChatBot