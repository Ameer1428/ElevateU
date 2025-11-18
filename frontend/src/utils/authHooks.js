import { useAuth, useUser } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'

/**
 * Custom hook for handling logout
 */
export const useLogout = () => {
  const { signOut } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await signOut()
      navigate('/')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return handleLogout
}

/**
 * Custom hook for user data and initials
 */
export const useUserData = () => {
  const { user } = useUser()
  const { userId } = useAuth()

  return {
    user,
    userId,
    fullName: user?.fullName || 'User',
    email: user?.primaryEmailAddress?.emailAddress || '',
  }
}