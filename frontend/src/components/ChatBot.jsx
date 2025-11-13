import { BubbleChat } from 'flowise-embed-react'
import { useAuth, useUser } from '@clerk/clerk-react'
import { useEffect, useState } from 'react'

const ChatBot = () => {
  const { userId, isSignedIn } = useAuth()
  const { user } = useUser()
  const [chatKey, setChatKey] = useState(0)

  useEffect(() => {
    if (isSignedIn && userId && user) {
      // Force chat re-render when user changes to reset session with new context
      setChatKey(prev => prev + 1)
    }
  }, [isSignedIn, userId, user])

  if (!isSignedIn) {
    return null
  }

  return (
    <BubbleChat
      key={chatKey}
      chatflowid="76037c3f-89d7-4a13-8719-09c180361eb2"
      apiHost="https://cloud.flowiseai.com"
      // Use userId as sessionId for user-specific conversations
      sessionId={`elevateu_${userId}`}
      // Pass user context that Flowise can access
      theme={{
        primaryColor: '#667eea',
        textColor: '#1e293b',
        backgroundColor: '#ffffff'
      }}
      // Additional user context that can be accessed in Flowise
      observersConfig={{
        userId: userId,
        userEmail: user?.primaryEmailAddress?.emailAddress || '',
        userName: user?.fullName || 'User',
        userFirstName: user?.firstName || 'User',
        platform: 'ElevateU'
      }}
    />
  )
}

export default ChatBot

