import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, useUser } from '@clerk/clerk-react'
import axios from 'axios'
import './StudentDashboard.css'

function StudentDashboard() {
  const { userId, signOut } = useAuth()
  const { user } = useUser()
  const navigate = useNavigate()
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('my-courses')

  useEffect(() => {
    if (userId) {
      fetchEnrollments()
    }
  }, [userId])

  const fetchEnrollments = async () => {
    try {
      // Ensure user exists in database
      await axios.post('/api/users', {
        clerkId: userId,
        email: user?.primaryEmailAddress?.emailAddress || '',
        name: user?.fullName || 'User',
        role: 'student'
      })

      const response = await axios.get(`/api/enrollments/user/${userId}`)
      setEnrollments(response.data)
    } catch (error) {
      console.error('Error fetching enrollments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await signOut()
    navigate('/')
  }

  const handleLogoClick = () => {
    navigate('/dashboard')
  }

  const handleAITutor = (courseId) => {
    // AI Tutor functionality - chatbot is already available via BubbleChat
    // Could open a modal or navigate to a dedicated chat page
    alert('AI Tutor is available via the chat bubble in the bottom right corner!')
  }

  const handleViewDetails = (courseId) => {
    navigate(`/course/${courseId}`)
  }

  const getInitials = (name) => {
    return name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="student-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
            <div className="logo-icon">📚</div>
            <span className="logo-text">ElevateU</span>
          </div>
        </div>
        <div className="header-right">
          <div className="user-profile">
            <div className="user-avatar">{getInitials(user?.fullName)}</div>
            <div className="user-info">
              <div className="user-name">{user?.fullName || 'User'}</div>
              <div className="user-email">{user?.primaryEmailAddress?.emailAddress || ''}</div>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout →
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="welcome-section">
          <h1 className="welcome-title">Welcome back, {user?.firstName || 'User'}! 👋</h1>
          <p className="welcome-subtitle">Continue your learning journey with AI-powered guidance</p>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'my-courses' ? 'active' : ''}`}
            onClick={() => setActiveTab('my-courses')}
          >
            My Courses
          </button>
          <button
            className={`tab ${activeTab === 'browse' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('browse')
              navigate('/browse')
            }}
          >
            Browse Courses
          </button>
        </div>

        <div className="courses-section">
          {enrollments.length === 0 ? (
            <div className="empty-state">
              <p>You haven't enrolled in any courses yet.</p>
              <button className="btn-primary" onClick={() => navigate('/browse')}>
                Browse Courses
              </button>
            </div>
          ) : (
            <div className="courses-grid">
              {enrollments.map((enrollment) => {
                const course = enrollment.course
                const progress = enrollment.progress
                const progressPercent = progress?.progress || 0
                const totalTopics = course?.topics?.length || 0
                const completedTopics = progress?.completedTopics?.length || 0

                return (
                  <div key={enrollment._id} className="course-card">
                    <div className="course-status">In Progress</div>
                    <h3 className="course-title">{course?.title}</h3>
                    <p className="course-description">{course?.description}</p>
                    <div className="course-meta">
                      <span>⏱ {course?.duration || 'N/A'}</span>
                      <span>✓ {totalTopics} topics</span>
                    </div>
                    <div className="progress-section">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${progressPercent}%`,
                            backgroundColor: progressPercent >= 50 ? '#3b82f6' : '#ef4444'
                          }}
                        />
                      </div>
                      <span className="progress-text">{Math.round(progressPercent)}% Complete</span>
                    </div>
                    <div className="course-actions">
                      <button
                        className="btn-ai-tutor"
                        onClick={() => handleAITutor(course?._id)}
                      >
                        💬 AI Tutor
                      </button>
                      <button
                        className="btn-view-details"
                        onClick={() => handleViewDetails(course?._id)}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default StudentDashboard

