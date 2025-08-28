// src/components/UserMenu.jsx

import React, { useState, useRef, useEffect } from "react";
import { 
  ChevronDown, User, LogOut, Settings, Shield, Key, X, Save, 
  Eye, EyeOff, Lock, Mail, AlertCircle, CheckCircle, Loader 
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const UserMenu = ({ firstName, lastName, role, email, onLogout, enhanced = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showCaptchaModal, setShowCaptchaModal] = useState(false);
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [captchaCredentials, setCaptchaCredentials] = useState({
    userId: '',
    password: ''
  });
  
  // Password Reset States
  const [resetStep, setResetStep] = useState('request'); // 'request', 'verify', 'newPassword', 'success'
  const [resetEmail, setResetEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetError, setResetError] = useState('');
  const [resendTimer, setResendTimer] = useState(0);
  
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Resend timer countdown
  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendTimer]);

  const getRoleColor = () => {
    switch (role) {
      case "admin":
        return "bg-purple-100 text-purple-700";
      case "owner":
        return "bg-red-100 text-red-700";
      default:
        return "bg-blue-100 text-blue-700";
    }
  };

  const getRoleIcon = () => {
    switch (role) {
      case "admin":
      case "owner":
        return <Shield className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  const handleOpenCaptchaModal = () => {
    setIsOpen(false);
    setShowCaptchaModal(true);
  };

  const handleSaveCaptchaCredentials = () => {
    console.log('Saving Death By Captcha credentials:', captchaCredentials);
    // TODO: Add API call to save credentials
    setShowCaptchaModal(false);
    setCaptchaCredentials({ userId: '', password: '' });
    setShowPassword(false);
  };

  const handleCloseCaptchaModal = () => {
    setShowCaptchaModal(false);
    setCaptchaCredentials({ userId: '', password: '' });
    setShowPassword(false);
  };

  // Password Reset Functions
  const handleOpenPasswordReset = () => {
    setIsOpen(false);
    setShowPasswordResetModal(true);
    setResetStep('request');
    setResetEmail(email || '');
    setResetError('');
  };

  const handleClosePasswordReset = () => {
    setShowPasswordResetModal(false);
    setResetStep('request');
    setResetEmail('');
    setVerificationCode('');
    setNewPassword('');
    setConfirmPassword('');
    setResetError('');
    setShowNewPassword(false);
    setShowConfirmPassword(false);
  };

  const handleRequestReset = async () => {
    setResetLoading(true);
    setResetError('');
    
    try {
      // TODO: Replace with your API endpoint
      // const response = await fetch('/api/password-reset/request', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email: resetEmail })
      // });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('Password reset requested for:', resetEmail);
      setResetStep('verify');
      setResendTimer(60); // 60 seconds before allowing resend
    } catch (error) {
      setResetError('Failed to send reset code. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    setResetLoading(true);
    setResetError('');
    
    try {
      // TODO: Replace with your API endpoint
      // const response = await fetch('/api/password-reset/verify', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email: resetEmail, code: verificationCode })
      // });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (verificationCode.length !== 6) {
        throw new Error('Invalid code');
      }
      
      console.log('Verification code validated:', verificationCode);
      setResetStep('newPassword');
    } catch (error) {
      setResetError('Invalid verification code. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (resendTimer > 0) return;
    
    setResetLoading(true);
    try {
      // TODO: Add API call to resend code
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Resending code to:', resetEmail);
      setResendTimer(60);
    } catch (error) {
      setResetError('Failed to resend code. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  const handleSetNewPassword = async () => {
    setResetError('');
    
    // Validation
    if (newPassword.length < 8) {
      setResetError('Password must be at least 8 characters long');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setResetError('Passwords do not match');
      return;
    }
    
    setResetLoading(true);
    
    try {
      // TODO: Replace with your API endpoint
      // const response = await fetch('/api/password-reset/update', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ 
      //     email: resetEmail, 
      //     code: verificationCode,
      //     newPassword: newPassword 
      //   })
      // });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('Password updated successfully');
      setResetStep('success');
      
      // Auto-close after 3 seconds
      setTimeout(() => {
        handleClosePasswordReset();
      }, 3000);
    } catch (error) {
      setResetError('Failed to update password. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <>
      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition ${
            enhanced ? "border border-gray-200" : ""
          }`}
        >
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-medium">
              {firstName?.[0]}{lastName?.[0]}
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-sm font-medium text-gray-900">
                {firstName} {lastName}
              </p>
              <p className={`text-xs px-1.5 py-0.5 rounded-full inline-flex items-center gap-1 ${getRoleColor()}`}>
                {getRoleIcon()}
                {role}
              </p>
            </div>
          </div>
          <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>

        {isOpen && (
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-sm font-medium text-gray-900">
                {firstName} {lastName}
              </p>
              <p className="text-xs text-gray-500">{role} account</p>
            </div>

            <a
              href="/UserProfileForm"
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <User className="h-4 w-4" />
              <span>Profile Settings</span>
            </a>

            <button
              onClick={handleOpenPasswordReset}
              className="w-full text-left flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <Lock className="h-4 w-4" />
              <span>Reset Password</span>
            </button>

            <button
              onClick={handleOpenCaptchaModal}
              className="w-full text-left flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <Key className="h-4 w-4" />
              <span>Death By Captcha Credentials</span>
            </button>

            {(role === "admin" || role === "owner") && (
              <a
                href="/admin"
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                <Settings className="h-4 w-4" />
                <span>Admin Panel</span>
              </a>
            )}

            <hr className="my-1 border-gray-100" />

            <button
              onClick={handleLogout}
              className="w-full text-left flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>

      {/* Death By Captcha Credentials Modal */}
      {showCaptchaModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Death By Captcha Credentials
              </h3>
              <button
                onClick={handleCloseCaptchaModal}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  User ID
                </label>
                <input
                  type="text"
                  value={captchaCredentials.userId}
                  onChange={(e) => setCaptchaCredentials({
                    ...captchaCredentials,
                    userId: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter your Death By Captcha user ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={captchaCredentials.password}
                    onChange={(e) => setCaptchaCredentials({
                      ...captchaCredentials,
                      password: e.target.value
                    })}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
              <button
                onClick={handleCloseCaptchaModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCaptchaCredentials}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                Save Credentials
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Password Reset Modal */}
      {showPasswordResetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Reset Password
              </h3>
              <button
                onClick={handleClosePasswordReset}
                disabled={resetLoading}
                className="text-gray-400 hover:text-gray-500 disabled:opacity-50"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6">
              {/* Step 1: Request Reset */}
              {resetStep === 'request' && (
                <div className="space-y-4">
                  <div className="text-center mb-4">
                    <Mail className="h-12 w-12 text-indigo-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      We'll send a verification code to your email address
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Enter your email"
                    />
                  </div>

                  {resetError && (
                    <div className="flex items-center gap-2 text-red-600 text-sm">
                      <AlertCircle className="h-4 w-4" />
                      {resetError}
                    </div>
                  )}
                </div>
              )}

              {/* Step 2: Verify Code */}
              {resetStep === 'verify' && (
                <div className="space-y-4">
                  <div className="text-center mb-4">
                    <Lock className="h-12 w-12 text-indigo-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      Enter the 6-digit code sent to {resetEmail}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Verification Code
                    </label>
                    <input
                      type="text"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      className="w-full px-3 py-2 text-center text-lg tracking-widest border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="000000"
                      maxLength="6"
                    />
                  </div>

                  <div className="text-center">
                    <button
                      onClick={handleResendCode}
                      disabled={resendTimer > 0 || resetLoading}
                      className="text-sm text-indigo-600 hover:text-indigo-700 disabled:text-gray-400"
                    >
                      {resendTimer > 0 
                        ? `Resend code in ${resendTimer}s` 
                        : 'Resend code'}
                    </button>
                  </div>

                  {resetError && (
                    <div className="flex items-center gap-2 text-red-600 text-sm">
                      <AlertCircle className="h-4 w-4" />
                      {resetError}
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: New Password */}
              {resetStep === 'newPassword' && (
                <div className="space-y-4">
                  <div className="text-center mb-4">
                    <Key className="h-12 w-12 text-indigo-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      Create a new secure password
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showNewPassword ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Enter new password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showNewPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? "text" : "password"}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Confirm new password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    Password must be at least 8 characters long
                  </div>

                  {resetError && (
                    <div className="flex items-center gap-2 text-red-600 text-sm">
                      <AlertCircle className="h-4 w-4" />
                      {resetError}
                    </div>
                  )}
                </div>
              )}

              {/* Step 4: Success */}
              {resetStep === 'success' && (
                <div className="text-center py-8">
                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    Password Reset Successfully!
                  </h4>
                  <p className="text-sm text-gray-600">
                    Your password has been updated. You can now log in with your new password.
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            {resetStep !== 'success' && (
              <div className="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
                <button
                  onClick={handleClosePasswordReset}
                  disabled={resetLoading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (resetStep === 'request') handleRequestReset();
                    else if (resetStep === 'verify') handleVerifyCode();
                    else if (resetStep === 'newPassword') handleSetNewPassword();
                  }}
                  disabled={resetLoading || 
                    (resetStep === 'request' && !resetEmail) ||
                    (resetStep === 'verify' && verificationCode.length !== 6) ||
                    (resetStep === 'newPassword' && (!newPassword || !confirmPassword))
                  }
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {resetLoading && <Loader className="h-4 w-4 animate-spin" />}
                  {resetStep === 'request' && 'Send Code'}
                  {resetStep === 'verify' && 'Verify'}
                  {resetStep === 'newPassword' && 'Update Password'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default UserMenu;