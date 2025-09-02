// src/components/AuthModal.jsx
import React, { useState, useEffect } from 'react';
import { X, Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

const AuthModal = ({ isOpen, onClose, view, onSwitchView, onLogin, onRegister }) => {
  const [isLogin, setIsLogin] = useState(view === 'login');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    confirmPassword: ''
  });

  // Reset form when modal opens/closes or view changes
  useEffect(() => {
    if (isOpen) {
      setShowPassword(false);
      // Keep form data to allow easy retry
    }
  }, [isOpen]);

  useEffect(() => {
    setIsLogin(view === 'login');
  }, [view]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const result = await onLogin(formData.email, formData.password);
        
        if (result.success) {
          // Show success toast
          toast.success('Login successful! Redirecting...', {
            duration: 2000,
            position: 'top-center',
          });
          
          // Clear form and close modal after short delay
          setTimeout(() => {
            setFormData({
              email: '',
              password: '',
              firstName: '',
              lastName: '',
              confirmPassword: ''
            });
            onClose();
          }, 500);
        } else {
          // Show error toast but keep modal open
          toast.error(result.error || 'Invalid email or password. Please check your credentials.', {
            duration: 4000,
            position: 'top-center',
          });
          
          // Clear only password for security but keep email for convenience
          setFormData(prev => ({ ...prev, password: '' }));
        }
      } else {
        // Registration logic
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match', {
            duration: 3000,
            position: 'top-center',
          });
          setLoading(false);
          return;
        }

        if (formData.password.length < 6) {
          toast.error('Password must be at least 6 characters', {
            duration: 3000,
            position: 'top-center',
          });
          setLoading(false);
          return;
        }

        const result = await onRegister({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName
        });

        if (result.success) {
          toast.success('Account created successfully! Welcome aboard!', {
            duration: 3000,
            position: 'top-center',
          });
          
          // Clear form and close modal after short delay
          setTimeout(() => {
            setFormData({
              email: '',
              password: '',
              firstName: '',
              lastName: '',
              confirmPassword: ''
            });
            onClose();
          }, 500);
        } else {
          // Show error toast but keep modal open
          toast.error(result.error || 'Registration failed. Please try again.', {
            duration: 4000,
            position: 'top-center',
          });
          
          // Keep all fields except passwords for retry
          setFormData(prev => ({ 
            ...prev, 
            password: '', 
            confirmPassword: '' 
          }));
        }
      }
    } catch (err) {
      console.error('Auth error:', err);
      toast.error('An unexpected error occurred. Please try again.', {
        duration: 4000,
        position: 'top-center',
      });
    } finally {
      setLoading(false);
    }
  };

  const switchView = () => {
    const newView = isLogin ? 'register' : 'login';
    setIsLogin(!isLogin);
    onSwitchView(newView);
    // Clear passwords when switching views
    setFormData(prev => ({ 
      ...prev, 
      password: '', 
      confirmPassword: '' 
    }));
  };

  const handleModalClose = () => {
    // Clear sensitive data when manually closing
    setFormData({
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      confirmPassword: ''
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={handleModalClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 animate-fade-in">
        {/* Close button */}
        <button
          onClick={handleModalClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
        
        {/* Header */}
        <div className="p-8 pb-0">
          <h2 className="text-2xl font-bold text-gray-900">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-gray-600 mt-1">
            {isLogin 
              ? 'Enter your credentials to access your account' 
              : 'Sign up to start automating your outreach'}
          </p>
        </div>
        
        {/* Form */}
        <form onSubmit={handleSubmit} className="p-8">
          {!isLogin && (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    required={!isLogin}
                    disabled={loading}
                    className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-50"
                    placeholder="John"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleChange}
                    required={!isLogin}
                    disabled={loading}
                    className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-50"
                    placeholder="Doe"
                  />
                </div>
              </div>
            </div>
          )}
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address *
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
                className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-50"
                placeholder="john@example.com"
                autoComplete="email"
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading}
                className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-50"
                placeholder="••••••••"
                autoComplete={isLogin ? "current-password" : "new-password"}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 disabled:opacity-50"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          
          {!isLogin && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required={!isLogin}
                  disabled={loading}
                  className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-50"
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
              </div>
            </div>
          )}
          
          {isLogin && (
            <div className="flex items-center justify-between mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-600">Remember me</span>
              </label>
              <a href="#" className="text-sm text-indigo-600 hover:text-indigo-700">
                Forgot password?
              </a>
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 font-semibold rounded-lg transition-all ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg transform hover:scale-[1.02]'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              isLogin ? 'Login' : 'Create Account'
            )}
          </button>
        </form>
        
        {/* Footer */}
        <div className="px-8 pb-8">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              {isLogin ? "Don't have an account?" : "Already have an account?"}
              {' '}
              <button
                type="button"
                onClick={switchView}
                disabled={loading}
                className="text-indigo-600 hover:text-indigo-700 font-semibold disabled:opacity-50"
              >
                {isLogin ? 'Sign Up' : 'Login'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;