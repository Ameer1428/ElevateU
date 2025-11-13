// import axios from 'axios';

// const API_BASE = import.meta.env.VITE_API_URL || "https://unrelevantly-statutory-chantay.ngrok-free.dev";

// const api = axios.create({
//   baseURL: API_BASE,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// // Add a request interceptor to handle errors
// api.interceptors.request.use(
//   (config) => {
//     console.log(`Making API call to: ${config.url}`);
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// // Add a response interceptor to handle errors
// api.interceptors.response.use(
//   (response) => {
//     console.log(`API Response from ${response.config.url}:`, response.data);
//     return response;
//   },
//   (error) => {
//     console.error('API Error:', error);
//     if (error.response) {
//       console.error('Error Response Data:', error.response.data);
//       console.error('Error Status:', error.response.status);
//     }
//     return Promise.reject(error);
//   }
// );

// export default api;
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || "https://elevateu-backend.loca.lt";

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

export default api;