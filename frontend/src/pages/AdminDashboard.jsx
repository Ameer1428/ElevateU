import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, useUser } from '@clerk/clerk-react'
import axios from 'axios'
import './AdminDashboard.css'

function AdminDashboard() {
  const { userId, signOut } = useAuth()
  const { user } = useUser()
  const navigate = useNavigate()
  const [stats, setStats] = useState({})
  const [courses, setCourses] = useState([])
  const [students, setStudents] = useState([])
  const [activeTab, setActiveTab] = useState('courses')
  const [loading, setLoading] = useState(true)
  const [showAddCourse, setShowAddCourse] = useState(false)

  useEffect(() => {
    if (userId) {
      fetchData()
    }
  }, [userId, activeTab])

  const fetchData = async () => {
    try {
      // Ensure admin user exists
      await axios.post('/api/users', {
        clerkId: userId,
        email: user?.primaryEmailAddress?.emailAddress || '',
        name: user?.fullName || 'Admin',
        role: 'admin'
      })

      const [statsRes, coursesRes, studentsRes] = await Promise.all([
        axios.get('/api/admin/stats'),
        axios.get('/api/courses'),
        axios.get('/api/admin/students')
      ])

      setStats(statsRes.data)
      setCourses(coursesRes.data)
      setStudents(studentsRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course?')) return

    try {
      await axios.delete(`/api/courses/${courseId}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting course:', error)
      alert('Failed to delete course')
    }
  }

  const handleViewStudent = (studentId) => {
    navigate(`/admin/student/${studentId}`)
  }

  const handleLogout = async () => {
    await signOut()
    navigate('/')
  }

  const handleLogoClick = () => {
    navigate('/admin')
  }

  const getInitials = (name) => {
    return name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'AD'
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="header-left">
          <div className="logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
            <div className="logo-icon">📚</div>
            <span className="logo-text">Admin Dashboard</span>
          </div>
        </div>
        <div className="header-right">
          <div className="admin-profile">
            <div className="admin-avatar">{getInitials(user?.fullName)}</div>
            <div className="admin-info">
              <div className="admin-name">Admin User</div>
              <div className="admin-role">Administrator</div>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout →
          </button>
        </div>
      </header>

      <div className="admin-content">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Courses</div>
            <div className="stat-value">{stats.totalCourses || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Active Students</div>
            <div className="stat-value">{stats.activeStudents || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Enrollments</div>
            <div className="stat-value">{stats.totalEnrollments || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg. Completion</div>
            <div className="stat-value">{stats.avgCompletion || 0}%</div>
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'courses' ? 'active' : ''}`}
            onClick={() => setActiveTab('courses')}
          >
            Course Management
          </button>
          <button
            className={`tab ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            Student Monitoring
          </button>
        </div>

        {activeTab === 'courses' && (
          <div className="courses-section">
            <div className="section-header">
              <h2 className="section-title">Manage Courses</h2>
              <button className="btn-add-course" onClick={() => setShowAddCourse(true)}>
                + Add Course
              </button>
            </div>
            {showAddCourse && (
              <AddCourseForm
                onClose={() => {
                  setShowAddCourse(false)
                  fetchData()
                }}
              />
            )}
            <div className="courses-grid">
              {courses.map((course) => (
                <div key={course._id} className="course-card">
                  <div className="course-actions-icons">
                    <button
                      className="icon-btn"
                      onClick={() => {
                        // Edit functionality - could open edit modal
                        alert('Edit functionality coming soon')
                      }}
                    >
                      ✏️
                    </button>
                    <button
                      className="icon-btn"
                      onClick={() => handleDeleteCourse(course._id)}
                    >
                      🗑️
                    </button>
                  </div>
                  <h3 className="course-title">{course.title}</h3>
                  <p className="course-description">{course.description}</p>
                  <div className="course-details">
                    <p><strong>Instructor:</strong> {course.instructor || 'TBA'}</p>
                    <p><strong>Duration:</strong> {course.duration || 'N/A'}</p>
                    <p><strong>Topics:</strong> {course.topics?.length || 0} topics</p>
                    <p><strong>Enrolled:</strong> {course.enrollmentCount || 0} students</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'students' && (
          <div className="students-section">
            <h2 className="section-title">Student Progress Monitoring</h2>
            <div className="students-list">
              {students.map((student) => (
                <div key={student._id} className="student-card">
                  <div className="student-header">
                    <div className="student-info">
                      <div className="student-avatar">{student.name?.substring(0, 2).toUpperCase() || 'U'}</div>
                      <div>
                        <div className="student-name">{student.name}</div>
                        <div className="student-email">{student.email}</div>
                      </div>
                    </div>
                    <button
                      className="btn-view-details"
                      onClick={() => handleViewStudent(student._id)}
                    >
                      👁️ View Details
                    </button>
                  </div>
                  <div className="student-tags">
                    <span className="tag">{student.enrollments || 0} Enrolled Courses</span>
                    <span className="tag">{student.avgProgress || 0}% Avg. Progress</span>
                  </div>
                  <div className="student-progress">
                    {student.courseProgress?.map((cp, idx) => (
                      <div key={idx} className="progress-item">
                        <div className="progress-header">
                          <span>{cp.courseTitle}</span>
                          <span>{cp.completedTopics}/{cp.totalTopics} topics</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${cp.progress}%`,
                              backgroundColor: cp.progress >= 50 ? '#3b82f6' : '#ef4444'
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function AddCourseForm({ onClose }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructor: '',
    duration: '',
    topics: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const topics = formData.topics.split('\n').filter(t => t.trim())
      await axios.post('/api/courses', {
        ...formData,
        topics: topics
      })
      onClose()
    } catch (error) {
      console.error('Error creating course:', error)
      alert('Failed to create course')
    }
  }

  return (
    <div className="add-course-modal">
      <div className="modal-content">
        <h2>Add New Course</h2>
        <p className="modal-subtitle">Create a new course with topics</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Course Title *</label>
            <input
              type="text"
              required
              placeholder="e.g., Introduction to Python"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Description *</label>
            <textarea
              required
              placeholder="Course description..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows="4"
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Instructor</label>
              <input
                type="text"
                placeholder="Instructor name"
                value={formData.instructor}
                onChange={(e) => setFormData({ ...formData, instructor: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Duration</label>
              <input
                type="text"
                placeholder="e.g., 8 weeks"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Topics (one per line)</label>
            <textarea
              placeholder="Python Basics&#10;Variables and Data Types&#10;Control Flow"
              value={formData.topics}
              onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
              rows="6"
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-create">Create Course</button>
            <button type="button" className="btn-cancel" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AdminDashboard

