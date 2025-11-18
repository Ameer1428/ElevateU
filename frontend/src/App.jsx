import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ClerkProvider, SignIn, SignUp } from '@clerk/clerk-react'
import LandingPage from './pages/LandingPage'
import StudentDashboard from './pages/StudentDashboard'
import BrowseCourses from './pages/BrowseCourses'
import CourseDetails from './pages/CourseDetails'
import AdminDashboard from './pages/AdminDashboard'
import StudentDetails from './pages/StudentDetails'
import ProtectedRoute from './components/ProtectedRoute'
import AuthLayout from './components/AuthLayout'
import ChatBot from './components/ChatBot'
import About from './pages/About'
import Contact from './pages/Contact'
import Footer from './pages/Footer'
import ScrollToTop from './pages/ScrollToTop'
import AfterAuth from './pages/AfterAuth'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || ''

function App() {
  if (!PUBLISHABLE_KEY) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Configuration Error</h1>
        <p>Please set VITE_CLERK_PUBLISHABLE_KEY in your .env file</p>
      </div>
    )
  }

  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <Router>
        <ScrollToTop />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route 
  path="/login/*" 
  element={
    <AuthLayout>
      <SignIn 
        routing="path" 
        path="/login"
        forceRedirectUrl="/after-auth"
      />
    </AuthLayout>
  }
/>

<Route 
  path="/signup/*" 
  element={
    <AuthLayout>
      <SignUp 
        routing="path" 
        path="/signup"
        forceRedirectUrl="/browse"
      />
    </AuthLayout>
  }
/>

          <Route path="/after-auth" element={<AfterAuth />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <StudentDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route
            path="/browse"
            element={
              <ProtectedRoute>
                <BrowseCourses />
              </ProtectedRoute>
            }
          />
          <Route
            path="/course/:courseId"
            element={
              <ProtectedRoute>
                <CourseDetails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requireAdmin>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/student/:studentId"
            element={
              <ProtectedRoute requireAdmin>
                <StudentDetails />
              </ProtectedRoute>
            }
          />
        </Routes>
        <ChatBot />
      </Router>
    </ClerkProvider>
    
  )
}

export default App