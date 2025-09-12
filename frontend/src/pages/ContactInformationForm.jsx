// src/pages/ContactInformationForm.jsx - Professional Enterprise Design
import React, { useState, useEffect, useRef } from "react";
import { 
  User, Mail, Phone, Globe, Building, MapPin, MessageSquare, 
  ChevronRight, Save, CheckCircle, AlertCircle, Briefcase, 
  Hash, FileText, Info, Target, Database, Clock, Zap, Shield, 
  Key, Lock, Camera, Upload, X, Edit3, Trash2, Settings,
  BarChart3, Activity, Bell, HelpCircle, Monitor, Workflow
} from "lucide-react";
import toast from 'react-hot-toast';
import api from '../services/api';
import useAuth from '../hooks/useAuth';

const ContactInformationForm = () => {
  const { user, updateUser } = useAuth();
  const [activeSection, setActiveSection] = useState("profile");
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    company_name: "",
    job_title: "",
    website_url: "",
    industry: "",
    subject: "Business Inquiry",
    message: "I am interested in your services and would like to discuss potential business opportunities.",
    city: "",
    state: "",
    zip_code: "",
    country: "",
    dbc_username: "",
    dbc_password: ""
  });
  const [saveStatus, setSaveStatus] = useState("");
  const [dbcBalance, setDbcBalance] = useState(null);
  const [checkingBalance, setCheckingBalance] = useState(false);
  const [profileImagePreview, setProfileImagePreview] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const fileInputRef = useRef(null);

  const sections = [
    {
      id: "profile",
      title: "Personal Profile",
      icon: User,
      description: "Basic personal information and contact details",
      fields: [
        { 
          id: "first_name", 
          label: "First Name", 
          type: "text", 
          required: true, 
          icon: User,
          editable: true,
          category: "identity"
        },
        { 
          id: "last_name", 
          label: "Last Name", 
          type: "text", 
          required: true, 
          icon: User,
          editable: true,
          category: "identity"
        },
        { 
          id: "email", 
          label: "Email Address", 
          type: "email", 
          required: true, 
          icon: Mail,
          editable: false,
          helper: "Email address is locked for security purposes",
          category: "identity"
        },
        { 
          id: "phone_number", 
          label: "Phone Number", 
          type: "tel", 
          icon: Phone,
          editable: true,
          category: "contact"
        }
      ]
    },
    {
      id: "business",
      title: "Business Information",
      icon: Building,
      description: "Professional details and company information",
      fields: [
        { 
          id: "company_name", 
          label: "Company Name", 
          type: "text", 
          icon: Building,
          editable: true,
          category: "company"
        },
        { 
          id: "job_title", 
          label: "Position/Title", 
          type: "text", 
          icon: Briefcase,
          editable: true,
          category: "company"
        },
        { 
          id: "website_url", 
          label: "Company Website", 
          type: "url", 
          icon: Globe,
          editable: true,
          category: "company"
        },
        { 
          id: "industry", 
          label: "Industry Sector", 
          type: "select",
          options: [
            "Technology & Software",
            "Healthcare & Medical",
            "Financial Services", 
            "Manufacturing",
            "Professional Services",
            "Education & Training",
            "Real Estate",
            "Marketing & Advertising",
            "Consulting",
            "Other"
          ],
          icon: Hash,
          editable: true,
          category: "company"
        }
      ]
    },
    {
      id: "automation",
      title: "Automation Settings",
      icon: Workflow,
      description: "Message templates and automation preferences",
      fields: [
        { 
          id: "subject", 
          label: "Default Subject Line", 
          type: "text", 
          icon: FileText,
          editable: true,
          category: "template"
        },
        { 
          id: "message", 
          label: "Message Template", 
          type: "textarea", 
          rows: 6, 
          icon: MessageSquare,
          editable: true,
          category: "template"
        }
      ]
    },
    {
      id: "security",
      title: "Security & Services",
      icon: Shield,
      description: "Third-party service configurations",
      fields: [
        { 
          id: "dbc_username", 
          label: "CAPTCHA Service Username", 
          type: "text", 
          icon: User,
          editable: true,
          category: "service"
        },
        { 
          id: "dbc_password", 
          label: "CAPTCHA Service Password", 
          type: "password", 
          icon: Lock,
          editable: true,
          category: "service"
        }
      ]
    },
    {
      id: "location",
      title: "Geographic Information",
      icon: MapPin,
      description: "Location details for enhanced targeting",
      fields: [
        { id: "city", label: "City", type: "text", icon: MapPin, editable: true, category: "location" },
        { id: "state", label: "State/Province", type: "text", icon: MapPin, editable: true, category: "location" },
        { id: "zip_code", label: "Postal Code", type: "text", icon: Hash, editable: true, category: "location" },
        { 
          id: "country", 
          label: "Country", 
          type: "select",
          options: ["United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "Japan", "Netherlands", "Sweden", "Switzerland", "Other"],
          icon: Globe,
          editable: true,
          category: "location"
        }
      ]
    }
  ];

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        ...Object.keys(prev).reduce((acc, key) => {
          acc[key] = user[key] || prev[key];
          return acc;
        }, {})
      }));
      
      if (user.profile_picture) {
        setProfileImagePreview(user.profile_picture);
      }
      
      if (user.dbc_username && user.dbc_password) {
        checkDbcBalance(user.dbc_username, user.dbc_password);
      }
    }
  }, [user]);

  const handleImageUpload = async (file) => {
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file');
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size must be less than 5MB');
      return;
    }
    
    setUploadingImage(true);
    
    try {
      const formDataImage = new FormData();
      formDataImage.append('profile_picture', file);
      
      const response = await api.post('/users/upload-avatar', formDataImage, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data?.profile_picture) {
        setProfileImagePreview(response.data.profile_picture);
        updateUser({ profile_picture: response.data.profile_picture });
        toast.success('Profile image updated successfully');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error('Failed to upload profile image');
    } finally {
      setUploadingImage(false);
    }
  };

  const checkDbcBalance = async (username, password) => {
    if (!username || !password) return;
    
    setCheckingBalance(true);
    try {
      const response = await api.post('/captcha/check-balance', { username, password });
      if (response.data?.balance !== undefined) {
        setDbcBalance(response.data.balance);
      }
    } catch (error) {
      console.error('Error checking DBC balance:', error);
      setDbcBalance(null);
    } finally {
      setCheckingBalance(false);
    }
  };

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
    
    if (id === 'dbc_username' || id === 'dbc_password') {
      if (formData.dbc_username && formData.dbc_password) {
        clearTimeout(window.dbcBalanceTimeout);
        window.dbcBalanceTimeout = setTimeout(() => {
          checkDbcBalance(
            id === 'dbc_username' ? value : formData.dbc_username,
            id === 'dbc_password' ? value : formData.dbc_password
          );
        }, 1500);
      }
    }
  };

  const handleSave = async () => {
    setSaveStatus("saving");
    
    try {
      // Prepare data payload for both tables
      const profileData = {
        // Fields that go to user_profiles table
        profile: {
          phone_number: formData.phone_number,
          company_name: formData.company_name,
          job_title: formData.job_title,
          website_url: formData.website_url,
          industry: formData.industry,
          subject: formData.subject,
          message: formData.message,
          city: formData.city,
          state: formData.state,
          zip_code: formData.zip_code,
          country: formData.country,
          dbc_username: formData.dbc_username,
          dbc_password: formData.dbc_password
        },
        // Fields that go to users table
        user: {
          first_name: formData.first_name,
          last_name: formData.last_name,
          // email is readonly, so we don't update it
        }
      };
      
      const response = await api.put('/users/profile', profileData);
      
      if (response.data?.success) {
        setSaveStatus("saved");
        toast.success('Profile updated successfully');
        
        // Update user context with the new data
        updateUser({ 
          first_name: formData.first_name,
          last_name: formData.last_name,
          ...formData 
        });
        
        // Re-check DBC balance if credentials were saved
        if (formData.dbc_username && formData.dbc_password) {
          checkDbcBalance(formData.dbc_username, formData.dbc_password);
        }
        
        setTimeout(() => setSaveStatus(""), 4000);
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      setSaveStatus("");
      toast.error('Failed to update profile');
    }
  };

  const currentSection = sections.find(s => s.id === activeSection);
  const SectionIcon = currentSection?.icon;

  const calculateProfileStrength = () => {
    const criticalFields = ['first_name', 'last_name', 'email', 'message'];
    const businessFields = ['company_name', 'job_title', 'industry'];
    const optionalFields = ['phone_number', 'website_url', 'subject'];
    
    const criticalScore = criticalFields.filter(field => formData[field]).length / criticalFields.length * 50;
    const businessScore = businessFields.filter(field => formData[field]).length / businessFields.length * 30;
    const optionalScore = optionalFields.filter(field => formData[field]).length / optionalFields.length * 20;
    
    return Math.round(criticalScore + businessScore + optionalScore);
  };

  const profileStrength = calculateProfileStrength();
  const hasCaptchaService = formData.dbc_username && formData.dbc_password;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              {/* Profile Image Section */}
              <div className="relative">
                <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-200 border-2 border-gray-300">
                  {profileImagePreview ? (
                    <img
                      src={profileImagePreview}
                      alt="Profile"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-600 flex items-center justify-center text-white font-semibold text-lg">
                      {formData.first_name?.[0]}{formData.last_name?.[0]}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingImage}
                  className="absolute -bottom-1 -right-1 w-6 h-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center text-xs shadow-lg transition-colors"
                >
                  {uploadingImage ? (
                    <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Camera className="w-3 h-3" />
                  )}
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e.target.files[0])}
                  className="hidden"
                />
              </div>
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Profile Management</h1>
                <p className="text-gray-600 text-sm mt-1">Configure your automation settings and personal information</p>
                {formData.first_name && formData.last_name && (
                  <div className="flex items-center space-x-3 mt-2">
                    <span className="text-sm font-medium text-blue-600">
                      {formData.first_name} {formData.last_name}
                    </span>
                    {formData.company_name && (
                      <span className="text-sm text-gray-500">• {formData.company_name}</span>
                    )}
                    {formData.job_title && (
                      <span className="text-sm text-gray-500">• {formData.job_title}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
            
            {/* Status Indicators */}
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="flex items-center space-x-2 mb-1">
                  <div className={`w-3 h-3 rounded-full ${profileStrength >= 80 ? 'bg-green-500' : profileStrength >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`} />
                  <span className="text-sm font-medium text-gray-700">Profile Strength</span>
                </div>
                <div className="text-lg font-bold text-gray-900">{profileStrength}%</div>
              </div>
              
              <div className="text-center">
                <div className="flex items-center space-x-2 mb-1">
                  <div className={`w-3 h-3 rounded-full ${hasCaptchaService ? 'bg-green-500' : 'bg-gray-400'}`} />
                  <span className="text-sm font-medium text-gray-700">CAPTCHA Service</span>
                </div>
                <div className="text-lg font-bold text-gray-900">
                  {hasCaptchaService ? 'Active' : 'Inactive'}
                </div>
                {dbcBalance !== null && (
                  <div className="text-xs text-gray-500">${dbcBalance.toFixed(2)}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-8">
          {/* Professional Sidebar Navigation */}
          <div className="col-span-12 lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden sticky top-8">
              <div className="p-4 bg-gray-50 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900 text-sm uppercase tracking-wide">Configuration Sections</h3>
              </div>
              <nav className="p-2">
                {sections.map((section) => {
                  const Icon = section.icon;
                  const isActive = activeSection === section.id;
                  const sectionFields = section.fields.filter(field => formData[field.id]);
                  const completion = Math.round((sectionFields.length / section.fields.length) * 100);
                  
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center justify-between p-3 rounded-md text-left transition-all ${
                        isActive 
                          ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                        <div>
                          <div className="font-medium text-sm">{section.title}</div>
                          <div className="text-xs text-gray-500 mt-0.5">{section.description}</div>
                          <div className="flex items-center mt-1">
                            <div className="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className={`h-full transition-all ${
                                  completion === 100 ? 'bg-green-500' : 
                                  completion > 50 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${completion}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500 ml-2">{completion}%</span>
                          </div>
                        </div>
                      </div>
                      {isActive && <ChevronRight className="w-4 h-4 text-blue-600" />}
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Professional Main Content */}
          <div className="col-span-12 lg:col-span-9">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Section Header */}
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <SectionIcon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{currentSection?.title}</h2>
                      <p className="text-gray-600 text-sm">{currentSection?.description}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Form Content */}
              <div className="p-6">
                {activeSection === 'security' && (
                  <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start space-x-3">
                      <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-blue-900 mb-1">CAPTCHA Service Integration</h4>
                        <p className="text-blue-800 text-sm leading-relaxed">
                          Integrate with Death By Captcha to automatically solve CAPTCHAs during form submissions. 
                          This service significantly improves success rates on protected websites.
                        </p>
                        <a 
                          href="https://deathbycaptcha.com" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-blue-700 hover:text-blue-800 text-sm font-medium mt-2"
                        >
                          <span>Create an account</span>
                          <ChevronRight className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {currentSection?.fields.map((field) => {
                    const FieldIcon = field.icon;
                    const isDisabled = !field.editable;
                    
                    return (
                      <div key={field.id} className={field.type === 'textarea' ? 'lg:col-span-2' : ''}>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <label className="block text-sm font-medium text-gray-700">
                              {field.label}
                              {field.required && <span className="text-red-500 ml-1">*</span>}
                            </label>
                            {isDisabled && (
                              <div className="flex items-center space-x-1 text-xs text-amber-600">
                                <Lock className="w-3 h-3" />
                                <span>Protected</span>
                              </div>
                            )}
                          </div>
                          
                          {field.helper && (
                            <p className="text-sm text-gray-500">{field.helper}</p>
                          )}
                          
                          <div className="relative">
                            <div className="absolute left-3 top-3 text-gray-400">
                              <FieldIcon className="w-5 h-5" />
                            </div>
                            
                            {field.type === 'textarea' ? (
                              <textarea
                                id={field.id}
                                rows={field.rows || 4}
                                value={formData[field.id] || ''}
                                onChange={handleChange}
                                disabled={isDisabled}
                                className={`w-full pl-11 pr-4 py-3 border rounded-lg text-sm resize-none transition-colors ${
                                  isDisabled 
                                    ? 'border-gray-200 bg-gray-50 text-gray-500 cursor-not-allowed' 
                                    : 'border-gray-300 bg-white hover:border-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                                }`}
                                placeholder={`Enter ${field.label.toLowerCase()}`}
                              />
                            ) : field.type === 'select' ? (
                              <select
                                id={field.id}
                                value={formData[field.id] || ''}
                                onChange={handleChange}
                                disabled={isDisabled}
                                className={`w-full pl-11 pr-4 py-3 border rounded-lg text-sm transition-colors ${
                                  isDisabled 
                                    ? 'border-gray-200 bg-gray-50 text-gray-500 cursor-not-allowed' 
                                    : 'border-gray-300 bg-white hover:border-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                                }`}
                              >
                                <option value="">Select {field.label}</option>
                                {field.options?.map(opt => (
                                  <option key={opt} value={opt}>{opt}</option>
                                ))}
                              </select>
                            ) : (
                              <input
                                type={field.type}
                                id={field.id}
                                value={formData[field.id] || ''}
                                onChange={handleChange}
                                disabled={isDisabled}
                                className={`w-full pl-11 pr-4 py-3 border rounded-lg text-sm transition-colors ${
                                  isDisabled 
                                    ? 'border-gray-200 bg-gray-50 text-gray-500 cursor-not-allowed' 
                                    : 'border-gray-300 bg-white hover:border-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                                }`}
                                placeholder={`Enter ${field.label.toLowerCase()}`}
                              />
                            )}
                            
                            {formData[field.id] && !isDisabled && (
                              <div className="absolute right-3 top-3">
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* CAPTCHA Service Test */}
                {activeSection === 'security' && (
                  <div className="mt-6 flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">Service Connection Test</h4>
                      <p className="text-sm text-gray-600">Verify your CAPTCHA service credentials</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      {dbcBalance !== null && (
                        <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 rounded-md">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-sm text-green-800">Connected (${dbcBalance.toFixed(2)})</span>
                        </div>
                      )}
                      <button
                        onClick={() => checkDbcBalance(formData.dbc_username, formData.dbc_password)}
                        disabled={checkingBalance || !formData.dbc_username || !formData.dbc_password}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          checkingBalance || !formData.dbc_username || !formData.dbc_password
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        }`}
                      >
                        {checkingBalance ? 'Testing...' : 'Test Connection'}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Professional Footer */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                <div>
                  {saveStatus === 'saved' && (
                    <div className="flex items-center space-x-2 text-green-600">
                      <CheckCircle className="w-5 h-5" />
                      <span className="text-sm font-medium">Profile updated successfully</span>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={handleSave}
                  disabled={saveStatus === 'saving'}
                  className={`px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
                    saveStatus === 'saving'
                      ? 'bg-gray-400 cursor-not-allowed text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                  }`}
                >
                  <Save className="w-4 h-4" />
                  <span>{saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </div>
            </div>

            {/* Professional Metrics */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Activity className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wide">Performance</span>
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">120/hr</div>
                <div className="text-sm text-gray-600">Forms processed per hour</div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <Target className="w-5 h-5 text-green-600" />
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wide">Success Rate</span>
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {hasCaptchaService ? '94%' : '72%'}
                </div>
                <div className="text-sm text-gray-600">
                  {hasCaptchaService ? 'With CAPTCHA service' : 'Standard processing'}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-yellow-600" />
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wide">Email Fallback</span>
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">8%</div>
                <div className="text-sm text-gray-600">When forms unavailable</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactInformationForm;