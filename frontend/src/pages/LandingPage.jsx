import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import './LandingPage.css'

function LandingPage() {
  const navigate = useNavigate()
  const { isSignedIn } = useAuth()

  const handleGetStarted = () => {
    if (isSignedIn) {
      navigate('/dashboard')
    } else {
      // Use Clerk's sign-in component
      const signInBtn = document.querySelector('.cl-signInButton')
      if (signInBtn) {
        signInBtn.click()
      } else {
        navigate('/sign-in')
      }
    }
  }

  const handleStartLearning = () => {
    if (isSignedIn) {
      navigate('/dashboard')
    } else {
      navigate('/sign-in')
    }
  }

  const handleAdminLogin = () => {
    if (isSignedIn) {
      navigate('/admin')
    } else {
      navigate('/sign-in')
    }
  }

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="logo">
          <span className="logo-text">ElevateU</span>
        </div>
        <button className="get-started-btn" onClick={handleGetStarted}>
          Get Started
        </button>
      </header>

      <section className="hero-section">
        <h1 className="hero-title">
          <span className="gradient-purple-blue">Transform Your Learning</span>
          <span className="gradient-pink-purple"> Journey with AI</span>
        </h1>
        <p className="hero-description">
          Experience personalized learning powered by advanced RAG technology. Track your progress, 
          get intelligent recommendations, and achieve your educational goals faster.
        </p>
        <div className="hero-buttons">
          <button className="btn-primary" onClick={handleStartLearning}>
            Start Learning
          </button>
          <button className="btn-secondary" onClick={handleAdminLogin}>
            Admin Login
          </button>
        </div>
      </section>

      <section className="features-section">
        <h2 className="section-title">Why Choose ElevateU?</h2>
        <p className="section-subtitle">Powerful features designed for modern learners and educators.</p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">Comprehensive Courses</h3>
            <p className="feature-description">
              Access a wide range of courses across multiple domains with structured learning paths.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3 className="feature-title">AI-Powered Tutor</h3>
            <p className="feature-description">
              Get personalized study recommendations using RAG-based AI that understands your progress.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3 className="feature-title">Progress Tracking</h3>
            <p className="feature-description">
              Monitor your learning journey with detailed analytics and progress visualization.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">👥</div>
            <h3 className="feature-title">Admin Dashboard</h3>
            <p className="feature-description">
              Comprehensive tools for course management and student progress monitoring.
            </p>
          </div>
        </div>
      </section>

      <section className="stats-section">
        <div className="stat-item">
          <div className="stat-number">1000+</div>
          <div className="stat-label">Active Students</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">50+</div>
          <div className="stat-label">Expert Courses</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">95%</div>
          <div className="stat-label">Success Rate</div>
        </div>
      </section>
    </div>
  )
}

export default LandingPage

