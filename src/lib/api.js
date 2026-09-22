import axios from 'axios';

/**
 * Base Axios instance for SKILLY frontend.
 * Reads base URL from environment variables.
 * Designed to communicate with the FastAPI backend at /api/v1.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to attach auth tokens (for future JWT implementation)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skilly_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for centralized error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If receiving 401 on non-login requests, clean up expired token
    if (error.response && error.response.status === 401) {
      const isLoginRequest = error.config && error.config.url && error.config.url.includes('/auth/login');
      if (!isLoginRequest) {
        localStorage.removeItem('skilly_auth_token');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
