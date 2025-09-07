// frontend/src/services/api.js

import axios from 'axios';

// Base URL for your FastAPI backend
const BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000, // 10 seconds timeout (reduced from 30s for faster debugging)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log(`[API] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status}:`, response.config.url);
    return response;
  },
  (error) => {
    console.error('[API] Response Error:', error);
    
    // Handle token expiration
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Don't redirect here, let the component handle it
    }
    
    return Promise.reject(error);
  }
);

export default api;