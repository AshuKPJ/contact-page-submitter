// frontend/src/hooks/useAuth.jsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);

  // Check if user is already logged in on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      console.log('Checking auth status with existing token...');
      // Verify token is still valid - FIXED ENDPOINT
      const response = await api.get('/auth/me');
      console.log('Auth check successful:', response.data);
      setUser(response.data);
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear invalid token
      localStorage.removeItem('access_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    if (loginLoading) {
      console.warn('Login already in progress');
      return false;
    }

    setLoginLoading(true);
    
    try {
      console.log('Starting login for:', email);
      console.log('API base URL:', api.defaults.baseURL);
      
      // Add a timeout specifically for the login request
      const response = await Promise.race([
        api.post('/auth/login', { email, password }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Login request timed out after 30 seconds')), 30000)
        )
      ]);

      console.log('Login response received:', response.data);

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        setUser(response.data.user);
        toast.success('Login successful!');
        return true;
      } else {
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      let errorMessage = 'Login failed';
      
      // Enhanced CORS error detection and messaging
      if (error.code === 'ERR_NETWORK' || 
          (error.message && error.message.toLowerCase().includes('network error'))) {
        errorMessage = 'Cannot connect to server. Please ensure the backend is running on port 8000 and check for CORS issues.';
        console.error('🔴 CORS/Network issue detected. Backend may not be running or CORS is blocking requests.');
        
        // Auto-run diagnostics
        if (window.apiDebug) {
          console.log('Running automatic diagnostics...');
          window.apiDebug.runFullTest(email, password).catch(console.error);
        }
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Login request timed out. Please check your connection and try again.';
      } else if (error.response?.status === 408) {
        errorMessage = 'Login request timed out. Please try again.';
      } else if (error.response?.status === 400) {
        errorMessage = error.response.data?.detail || 'Invalid login credentials';
      } else if (error.response?.status === 422) {
        errorMessage = 'Invalid email or password format';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      return false;
    } finally {
      setLoginLoading(false);
    }
  };

  const register = async (userData) => {
    if (loginLoading) {
      console.warn('Registration already in progress');
      return false;
    }

    setLoginLoading(true);
    
    try {
      console.log('Starting registration for:', userData.email);
      
      // Add timeout for registration too
      const response = await Promise.race([
        api.post('/auth/register', userData),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Registration request timed out after 30 seconds')), 30000)
        )
      ]);

      console.log('Registration response received:', response.data);

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        setUser(response.data.user);
        toast.success('Registration successful!');
        return true;
      } else {
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Registration failed';
      
      // Enhanced CORS error detection for registration
      if (error.code === 'ERR_NETWORK' || 
          (error.message && error.message.toLowerCase().includes('network error'))) {
        errorMessage = 'Cannot connect to server. Please ensure the backend is running on port 8000.';
        console.error('🔴 CORS/Network issue during registration. Backend may not be running.');
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Registration request timed out. Please try again.';
      } else if (error.response?.status === 408) {
        errorMessage = 'Registration request timed out. Please try again.';
      } else if (error.response?.status === 400) {
        errorMessage = error.response.data?.detail || 'Registration failed - invalid data';
      } else if (error.response?.status === 409) {
        errorMessage = 'Email already exists. Please use a different email or try logging in.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Invalid registration data format';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      return false;
    } finally {
      setLoginLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    loading,
    loginLoading,
    login,
    register,
    logout,
    checkAuthStatus
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}