import { useNavigate } from 'react-router-dom'

const AuthLayout = ({ children, title }) => {
  const navigate = useNavigate()

  const handleLogoClick = () => {
    navigate('/')
  }

  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-header">
          <div className="logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
            <span className="logo-text">ElevateU</span>
          </div>
          <h1 className="auth-title">{title}</h1>
          <p className="auth-subtitle">Welcome to AI-powered learning</p>
        </div>
        <div className="auth-content">
          {children}
        </div>
      </div>
    </div>
  )
}

export default AuthLayout