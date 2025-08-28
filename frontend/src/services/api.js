// src/services/api.js

import axios from "axios";

// Determine API base URL
const getApiBaseUrl = () => {
  // Check environment variable first
  if (import.meta.env.VITE_API_BASE) {
    console.log('Using API base from env:', import.meta.env.VITE_API_BASE);
    return import.meta.env.VITE_API_BASE;
  }
  
  // Default to localhost for development
  const { protocol, hostname, port } = window.location;
  
  let apiUrl;
  if (port === "5173" || port === "3000") {
    // Development mode - backend on port 8000
    apiUrl = `${protocol}//${hostname}:8000`;
  } else {
    // Production - use same origin
    apiUrl = `${protocol}//${hostname}${port ? ":" + port : ""}`;
  }
  
  console.log('Using computed API base URL:', apiUrl);
  return apiUrl;
};

const api = axios.create({
  baseURL: getApiBaseUrl() + "/api",
  timeout: 30000, // 30 second timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token and logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add timestamp to track request duration
    config.metadata = { startTime: new Date() };
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const endTime = new Date();
    const duration = endTime.getTime() - response.config.metadata.startTime.getTime();
    
    console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${duration}ms)`);
    
    return response;
  },
  (error) => {
    // Calculate request duration for failed requests too
    if (error.config?.metadata?.startTime) {
      const endTime = new Date();
      const duration = endTime.getTime() - error.config.metadata.startTime.getTime();
      console.log(`❌ ${error.config.method?.toUpperCase()} ${error.config.url} failed after ${duration}ms`);
    }
    
    // Enhanced error logging
    if (error.response) {
      // Server responded with error status
      console.error(`Server error ${error.response.status}:`, error.response.data);
      
      if (error.response.status === 401) {
        console.log('Unauthorized - clearing token and redirecting');
        localStorage.removeItem("access_token");
        // Only redirect if we're not already on the login page
        if (window.location.pathname !== "/") {
          window.location.href = "/";
        }
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received:', error.request);
      console.error('This usually means:', [
        '1. Backend server is not running on port 8000',
        '2. Network connectivity issues',
        '3. CORS issues',
        '4. Backend is hanging/not responding'
      ]);
    } else {
      // Something else happened
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Debug helper functions
export const debugApi = {
  // Test basic connectivity
  testConnection: async () => {
    try {
      console.log('Testing API connection...');
      const response = await api.get('/health');
      console.log('✅ API connection successful:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('❌ API connection failed:', error.message);
      return { success: false, error: error.message };
    }
  },
  
  // Test database connectivity
  testDatabase: async () => {
    try {
      console.log('Testing database connection...');
      const response = await api.get('/debug/db');
      console.log('✅ Database connection successful:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('❌ Database connection failed:', error.message);
      return { success: false, error: error.message };
    }
  },
  
  // Test login endpoint specifically
  testLogin: async (email, password) => {
    try {
      console.log('Testing login endpoint with debug version...');
      const response = await api.post('/debug/login-test', { email, password });
      console.log('✅ Login test successful:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('❌ Login test failed:', error.message);
      return { 
        success: false, 
        error: error.response?.data || error.message 
      };
    }
  },
  
  // Get current API configuration
  getConfig: () => {
    return {
      baseURL: api.defaults.baseURL,
      timeout: api.defaults.timeout,
      currentToken: localStorage.getItem("access_token") ? "Present" : "None"
    };
  },

  // Test all endpoints in sequence
  runFullTest: async (email, password) => {
    console.log('🔍 Running full API diagnostic...');
    
    const results = {
      health: await debugApi.testConnection(),
      database: await debugApi.testDatabase(),
      login: email && password ? await debugApi.testLogin(email, password) : null,
      config: debugApi.getConfig()
    };
    
    console.log('📊 Full test results:', results);
    return results;
  }
};

// Make debug functions available in development
if (import.meta.env.MODE === 'development') {
  window.apiDebug = debugApi;
  window.api = api;
  console.log('🔧 API debug tools available:');
  console.log('  - window.apiDebug.testConnection()');
  console.log('  - window.apiDebug.testDatabase()');
  console.log('  - window.apiDebug.testLogin(email, password)');
  console.log('  - window.apiDebug.runFullTest(email, password)');
  console.log('  - window.apiDebug.getConfig()');
}

export default api;