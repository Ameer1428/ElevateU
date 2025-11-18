import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || "https://unrelevantly-statutory-chantay.ngrok-free.dev";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add a request interceptor to handle errors
api.interceptors.request.use(
  (config) => {
    console.log(`Making API call to: ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    console.log(`API Success from ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.message);
    if (error.response) {
      console.error('Error Status:', error.response.status);
      console.error('Error Data:', error.response.data);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// Admin API functions with authentication
export const adminApi = {
  // Get admin stats
  getStats: (userId) => {
    return api.get('/api/admin/stats', {
      headers: {
        'X-Admin-Key': 'elevateu-admin-2024',
        'X-User-ID': userId
      }
    });
  },

  // Get all students
  getStudents: (userId) => {
    return api.get('/api/admin/students', {
      headers: {
        'X-Admin-Key': 'elevateu-admin-2024',
        'X-User-ID': userId
      }
    });
  },

  // Get student details
  getStudentDetails: (studentId, userId) => {
    return api.get(`/api/admin/student/${studentId}`, {
      headers: {
        'X-Admin-Key': 'elevateu-admin-2024',
        'X-User-ID': userId
      }
    });
  },

  // Delete course
  deleteCourse: (courseId, userId) => {
    return api.delete(`/api/courses/${courseId}`, {
      headers: {
        'X-Admin-Key': 'elevateu-admin-2024',
        'X-User-ID': userId
      }
    });
  },

  // Create course
  createCourse: (courseData, userId) => {
    return api.post('/api/courses', courseData, {
      headers: {
        'X-Admin-Key': 'elevateu-admin-2024',
        'X-User-ID': userId
      }
    });
  }
};

export default api;