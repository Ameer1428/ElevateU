import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import axios from 'axios'
import './StudentDetails.css'

function StudentDetails() {
  const { studentId } = useParams()
  const navigate = useNavigate()
  const [student, setStudent] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStudentDetails()
  }, [studentId])

  const fetchStudentDetails = async () => {
    try {
      const response = await axios.get(`/api/admin/student/${studentId}`)
      setStudent(response.data)
    } catch (error) {
      console.error('Error fetching student details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyUpdate = async (updateId, comment) => {
    try {
      await axios.put(`/api/study-updates/${updateId}/verify`, {
        adminComment: comment
      })
      fetchStudentDetails()
    } catch (error) {
      console.error('Error verifying update:', error)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!student) {
    return <div className="error">Student not found</div>
  }

  return (
    <div className="student-details">
      <div className="details-header">
        <button className="back-btn" onClick={() => navigate('/admin')}>
          ← Back to Dashboard
        </button>
        <h1 className="page-title">Student Details</h1>
      </div>

      <div className="details-content">
        <div className="student-profile-card">
          <div className="profile-left">
            <div className="profile-avatar">
              {student.name?.substring(0, 2).toUpperCase() || 'U'}
            </div>
            <div className="profile-info">
              <div className="profile-name">{student.name}</div>
              <div className="profile-email">{student.email}</div>
            </div>
          </div>
          <div className="profile-right">
            <div className="enrollments-badge">
              {student.enrollments?.length || 0} Enrolled Courses
            </div>
          </div>
        </div>

        <div className="details-grid">
          <div className="left-column">
            <h2 className="section-title">Course Progress</h2>
            {student.enrollments?.map((enrollment, idx) => {
              const course = enrollment.course
              const progress = enrollment.progress
              const progressPercent = progress?.progress || 0
              const completedTopics = progress?.completedTopics || []
              const totalTopics = course?.topics?.length || 0

              return (
                <div key={idx} className="course-progress-card">
                  <h3 className="course-title">{course?.title}</h3>
                  <p className="course-description">{course?.description}</p>
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
                    <div className="progress-info">
                      <span>{Math.round(progressPercent)}% Complete</span>
                      <span>Covered Topics: {completedTopics.length}/{totalTopics}</span>
                    </div>
                    <div className="progress-meta">
                      <span>Last Updated: {progress?.lastUpdated?.split('T')[0] || 'N/A'}</span>
                      <span className="status-badge">In Progress</span>
                    </div>
                  </div>
                  <div className="topics-list">
                    <h4 className="topics-title">Topics Breakdown:</h4>
                    {course?.topics?.map((topic, topicIdx) => {
                      const isCompleted = completedTopics.includes(topicIdx)
                      return (
                        <div key={topicIdx} className="topic-item">
                          <span className={isCompleted ? 'topic-checked' : 'topic-unchecked'}>
                            {isCompleted ? '✓' : '○'}
                          </span>
                          <span className={isCompleted ? 'topic-completed' : ''}>
                            {topic}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="right-column">
            <h2 className="section-title">Daily Study Updates</h2>
            {student.studyUpdates?.map((update, idx) => (
              <div key={idx} className="update-card">
                <div className="update-header">
                  <h3 className="update-course-title">{update.course?.title}</h3>
                  {update.verified && (
                    <span className="verified-badge">Verified</span>
                  )}
                </div>
                <div className="update-date">{update.date?.split('T')[0] || 'N/A'}</div>
                <p className="update-content">{update.content}</p>
                {update.verified && update.adminComment && (
                  <div className="admin-comment">
                    <strong>Admin Verification:</strong> {update.adminComment}
                  </div>
                )}
              </div>
            ))}
            {(!student.studyUpdates || student.studyUpdates.length === 0) && (
              <div className="empty-updates">No study updates yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StudentDetails

