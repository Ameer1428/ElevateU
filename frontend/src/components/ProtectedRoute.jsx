import { useAuth } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'  

function ProtectedRoute({ children, requireAdmin = false }) {
  const { isLoaded, userId, isSignedIn, user } = useAuth()
  const [userData, setUserData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoaded && isSignedIn && userId) {
      const fetchUser = async () => {
        try {
          const email = user?.primaryEmailAddress?.emailAddress || ''
          const name = user?.fullName || 'User'
          
          const response = await api.post('/api/users', {
            clerkId: userId,
            email: email,
            name: name,
            role: requireAdmin ? 'admin' : 'student'
          })
          setUserData(response.data)
        } catch (error) {
          console.error('Error fetching user:', error)
        } finally {
          setLoading(false)
        }
      }
      fetchUser()
    } else if (isLoaded && !isSignedIn) {
      setLoading(false)
    }
  }, [isLoaded, isSignedIn, userId, requireAdmin, user])

  if (!isLoaded || loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.25rem',
        color: '#64748b'
      }}>
        Loading...
      </div>
    )
  }

  if (!isSignedIn) {
    return <Navigate to="/" replace />
  }

  if (requireAdmin && userData && userData.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default ProtectedRoute
