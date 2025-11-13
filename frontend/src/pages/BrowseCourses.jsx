import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, useUser } from '@clerk/clerk-react'
import api from '../services/api'
import './BrowseCourses.css'

function BrowseCourses() {
  const { userId } = useAuth()
  const { user } = useUser()
  const navigate = useNavigate()
  const [courses, setCourses] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCourses()
    fetchEnrollments()
  }, [userId])

  const fetchCourses = async () => {
    try {
      const response = await api.get('/api/courses')
      setCourses(response.data)
    } catch (error) {
      console.error('Error fetching courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchEnrollments = async () => {
    if (!userId) return
    try {
      const response = await api.get(`/api/enrollments/user/${userId}`)
      setEnrollments(response.data.map(e => e.courseId))
    } catch (error) {
      console.error('Error fetching enrollments:', error)
    }
  }

  const handleEnroll = async (courseId) => {
    if (!userId) {
      navigate('/')
      return
    }

    try {
      await api.post('/api/enrollments', {
        userId: userId,
        courseId: courseId
      })
      await fetchEnrollments()
      navigate(`/course/${courseId}`)
    } catch (error) {
      console.error('Error enrolling:', error)
      alert('Failed to enroll in course')
    }
  }

  const handleLogoClick = () => {
    navigate('/dashboard')
  }

  const getInitials = (name) => {
    return name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="browse-courses">
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
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
          <button className="logout-btn" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
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
            className="tab"
            onClick={() => navigate('/dashboard')}
          >
            My Courses
          </button>
          <button className="tab active">
            Browse Courses
          </button>
        </div>

        <div className="courses-section">
          {courses.length === 0 ? (
            <div className="empty-state">
              <p>No courses available at the moment.</p>
            </div>
          ) : (
            <div className="courses-grid">
              {courses.map((course) => {
                const isEnrolled = enrollments.includes(course._id)
                
                return (
                  <div key={course._id} className="course-card">
                    <h3 className="course-title">{course.title}</h3>
                    <p className="course-description">{course.description}</p>
                    <div className="course-details">
                      <p><strong>Instructor:</strong> {course.instructor || 'TBA'}</p>
                      <p><strong>Duration:</strong> {course.duration || 'N/A'}</p>
                      <p><strong>Topics:</strong> {course.topics?.length || 0} topics</p>
                    </div>
                    <button
                      className="btn-enroll"
                      onClick={() => handleEnroll(course._id)}
                      disabled={isEnrolled}
                    >
                      {isEnrolled ? 'Already Enrolled' : 'Enroll Now'}
                    </button>
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

export default BrowseCourses