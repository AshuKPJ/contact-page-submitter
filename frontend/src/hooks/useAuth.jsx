// frontend/src/hooks/useAuth.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);

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

      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('access_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    console.log('[LOGIN] Attempting login for:', email);
    
    try {
      const response = await api.post('/auth/login', { 
        email: email.trim().toLowerCase(), 
        password 
      });
      
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        setUser(response.data.user);
        console.log('[LOGIN] Success');
        return { success: true };
      }
      
      return { success: false, error: 'No token received' };
    } catch (error) {
      console.error('[LOGIN] Error:', error);
      
      // Determine error message
      let errorMessage = 'Login failed. Please try again.';
      
      if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Cannot connect to server. Is it running on port 8000?';
      } else if (error.response) {
        switch (error.response.status) {
          case 401:
            errorMessage = 'Invalid email or password. Please check your credentials.';
            break;
          case 403:
            errorMessage = 'Your account is restricted. Please contact support.';
            break;
          case 404:
            errorMessage = 'Login service not found. Please try again later.';
            break;
          case 500:
            errorMessage = 'Server error. Please try again in a moment.';
            break;
          default:
            errorMessage = error.response.data?.detail || 'Login failed. Please try again.';
        }
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    console.log('[REGISTER] Attempting registration for:', userData.email);
    
    try {
      const response = await api.post('/auth/register', {
        ...userData,
        email: userData.email.trim().toLowerCase()
      });
      
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        setUser(response.data.user);
        console.log('[REGISTER] Success');
        return { success: true };
      }
      
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      console.error('[REGISTER] Error:', error);
      
      let errorMessage = 'Registration failed. Please try again.';
      
      if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Cannot connect to server. Is it running on port 8000?';
      } else if (error.response) {
        switch (error.response.status) {
          case 400:
            errorMessage = 'Invalid information. Please check all fields.';
            break;
          case 409:
            errorMessage = 'This email is already registered. Please login instead.';
            break;
          case 422:
            errorMessage = 'Please fill all required fields correctly.';
            break;
          case 500:
            errorMessage = 'Server error. Please try again later.';
            break;
          default:
            errorMessage = error.response.data?.detail || 'Registration failed.';
        }
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    window.location.href = '/';
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