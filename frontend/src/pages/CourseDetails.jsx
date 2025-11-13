import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth, useUser } from '@clerk/clerk-react'
import api from '../services/api'
import './CourseDetails.css'

function CourseDetails() {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const { userId } = useAuth()
  const { user } = useUser()
  const [course, setCourse] = useState(null)
  const [progress, setProgress] = useState(null)
  const [completedTopics, setCompletedTopics] = useState([])
  const [loading, setLoading] = useState(true)
  const [notEnrolled, setNotEnrolled] = useState(false)

  useEffect(() => {
    if (!courseId || !userId) return
    initialize()
  }, [courseId, userId])

  const initialize = async () => {
    try {
      // Ensure user exists
      await api.post('/api/users', {
        clerkId: userId,
        email: user?.primaryEmailAddress?.emailAddress || '',
        name: user?.fullName || 'User',
        role: 'student'
      })

      const courseRes = await api.get(`/api/courses/${courseId}`)
      setCourse(courseRes.data)

      try {
        const progRes = await api.get(`/api/progress/user/${userId}/course/${courseId}`)
        setProgress(progRes.data)
        setCompletedTopics(progRes.data?.completedTopics || [])
        setNotEnrolled(false)
      } catch (err) {
        // If progress not found, user may not be enrolled
        setNotEnrolled(true)
      }
    } catch (error) {
      console.error('Error loading course details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEnroll = async () => {
    try {
      await api.post('/api/enrollments', {
        userId: userId,
        courseId: courseId
      })
      setNotEnrolled(false)
      // Fetch progress after enrollment
      const progRes = await api.get(`/api/progress/user/${userId}/course/${courseId}`)
      setProgress(progRes.data)
      setCompletedTopics(progRes.data?.completedTopics || [])
    } catch (error) {
      console.error('Error enrolling:', error)
      alert('Failed to enroll in course')
    }
  }

  const toggleTopic = async (topicIdx) => {
    if (!userId) return
    const nextCompleted = completedTopics.includes(topicIdx)
      ? completedTopics.filter((t) => t !== topicIdx)
      : [...completedTopics, topicIdx]

    try {
      const res = await api.post('/api/progress', {
        userId: userId,
        courseId: courseId,
        completedTopics: nextCompleted
      })
      setCompletedTopics(nextCompleted)
      setProgress(res.data)
    } catch (error) {
      console.error('Error updating progress:', error)
      alert('Failed to update progress')
    }
  }

  const handleBack = () => navigate('/dashboard')

  const getInitials = (name) => {
    return name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!course) {
    return (
      <div className="loading">Course not found</div>
    )
  }

  const progressPercent = progress?.progress || 0
  const totalTopics = course?.topics?.length || 0

  return (
    <div className="course-details-page">
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo" onClick={handleBack} style={{ cursor: 'pointer' }}>
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
          <button className="logout-btn" onClick={handleBack}>
            Back to Dashboard
          </button>
        </div>
      </header>

      <div className="course-content">
        <div className="course-hero">
          <h1 className="course-title">{course?.title}</h1>
          <p className="course-description">{course?.description}</p>
          <div className="course-meta">
            <span>⏱ {course?.duration || 'N/A'}</span>
            <span>✓ {totalTopics} topics</span>
          </div>
          {notEnrolled ? (
            <button className="btn-primary" onClick={handleEnroll}>
              Enroll to Start
            </button>
          ) : (
            <div className="progress-section">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.round(progressPercent)}%`,
                    backgroundColor: progressPercent >= 50 ? '#3b82f6' : '#ef4444'
                  }}
                />
              </div>
              <span className="progress-text">{Math.round(progressPercent)}% Complete</span>
            </div>
          )}
        </div>

        {!notEnrolled && (
          <div className="topics-section">
            <h2 className="section-title">Topics</h2>
            <div className="topics-list">
              {course?.topics?.map((topic, idx) => {
                const isCompleted = completedTopics.includes(idx)
                return (
                  <label key={idx} className="topic-item">
                    <input
                      type="checkbox"
                      checked={isCompleted}
                      onChange={() => toggleTopic(idx)}
                    />
                    <span className={isCompleted ? 'topic-completed' : ''}>{topic}</span>
                  </label>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CourseDetails