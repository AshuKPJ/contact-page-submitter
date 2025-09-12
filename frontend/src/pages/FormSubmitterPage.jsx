// src/pages/FormSubmitterPage.jsx - Enhanced Integration with Backend
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, FileText, CheckCircle, Loader, X, AlertCircle, 
  ArrowRight, Clock, Globe, Mail, Zap, Target, Activity,
  ChevronRight, Database, Shield, TrendingUp, Play, Info,
  FileSpreadsheet, Users, BarChart3, Award, Sparkles,
  Check, AlertTriangle, Cpu, Send, Settings, Rocket
} from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const FormSubmitterPage = () => {
  const navigate = useNavigate();
  const [csvFile, setCsvFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [csvPreview, setCsvPreview] = useState(null);
  const [campaignActive, setCampaignActive] = useState(false);
  const [parseError, setParseError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [campaignName, setCampaignName] = useState('');
  const [campaignMessage, setCampaignMessage] = useState('');
  const [campaignId, setCampaignId] = useState(null);
  const [realTimeProgress, setRealTimeProgress] = useState(null);
  const [campaignSettings, setCampaignSettings] = useState({
    skipDuplicates: true,
    emailFallback: true,
    captchaHandling: true,
    delayBetweenSubmissions: 30,
    proxy: '',
    haltOnCaptcha: true
  });
  const fileInputRef = useRef(null);
  const pollIntervalRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const parseCSV = (text) => {
    const lines = text.trim().split('\n');
    if (lines.length === 0) return null;

    // Get headers from first line
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    // Check if 'website' column exists
    const websiteIndex = headers.findIndex(h => 
      h.toLowerCase().includes('website') || 
      h.toLowerCase().includes('url') ||
      h.toLowerCase().includes('domain') ||
      h.toLowerCase().includes('site')
    );

    if (websiteIndex === -1) {
      throw new Error("CSV must contain a 'website', 'url', 'domain', or 'site' column");
    }

    // Parse data rows
    const rows = [];
    for (let i = 1; i < Math.min(lines.length, 6); i++) { // Show first 5 rows
      const columns = lines[i].split(',').map(c => c.trim().replace(/"/g, ''));
      if (columns[websiteIndex] && columns[websiteIndex].length > 0) {
        rows.push(columns);
      }
    }

    return {
      headers,
      rows,
      totalRows: Math.max(0, lines.length - 1), // Total rows minus header
      websiteColumnIndex: websiteIndex,
      websiteColumnName: headers[websiteIndex]
    };
  };

  const handleFile = async (file) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setParseError('Please select a CSV file');
      toast.error('Please select a CSV file');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      setParseError('File size must be less than 10MB');
      toast.error('File size must be less than 10MB');
      return;
    }
    
    setParseError(null);
    setCsvFile(file);
    
    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setUploadProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
      }
    }, 100);
    
    try {
      // Read the file content
      const text = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Failed to read file'));
        reader.readAsText(file);
      });

      // Parse CSV content
      const parsedData = parseCSV(text);
      
      if (!parsedData) {
        throw new Error('Failed to parse CSV file');
      }

      setCsvPreview(parsedData);
      
      // Auto-generate campaign name
      const timestamp = new Date().toISOString().slice(0, 10);
      setCampaignName(`Campaign - ${file.name.replace('.csv', '')} - ${timestamp}`);
      
      // Default message
      setCampaignMessage("Hello, I'm interested in learning more about your services and would like to discuss potential business opportunities. Please let me know the best time to connect. Thank you!");
      
      toast.success(`Successfully loaded ${parsedData.totalRows} websites`);
      
    } catch (error) {
      console.error('Error parsing CSV:', error);
      setParseError(error.message || 'Failed to parse CSV file');
      setCsvFile(null);
      setCsvPreview(null);
      toast.error(error.message || 'Failed to parse CSV file');
    }
  };

  const startPollingProgress = (campaignId) => {
    // Clear any existing interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    // Start polling for campaign status
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await api.get(`/submissions/status/${campaignId}`);
        const progress = response.data;
        
        setRealTimeProgress(progress);
        
        // Stop polling when campaign is complete
        if (progress.status === 'completed' || progress.campaign_status === 'completed') {
          clearInterval(pollIntervalRef.current);
          toast.success('Campaign completed successfully!');
          setTimeout(() => {
            navigate('/campaigns');
          }, 2000);
        }
      } catch (error) {
        console.error('Error polling campaign status:', error);
        // Continue polling even on errors, but limit retries
      }
    }, 3000); // Poll every 3 seconds
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!csvFile) {
      toast.error('Please select a CSV file');
      return;
    }

    if (!campaignName.trim()) {
      toast.error('Please enter a campaign name');
      return;
    }
    
    setSubmitting(true);
    const toastId = toast.loading('Creating campaign...');
    
    try {
      // Step 1: Create campaign
      const campaignData = {
        name: campaignName,
        message: campaignMessage || "I'm interested in your services and would like to discuss business opportunities."
      };

      const campaignResponse = await api.post('/campaigns', campaignData);
      const newCampaignId = campaignResponse.data.id;
      setCampaignId(newCampaignId);

      toast.success('Campaign created!', { id: toastId });
      toast.loading('Starting automated processing...', { id: toastId });

      // Step 2: Upload CSV and start processing using your existing endpoint
      const formData = new FormData();
      formData.append('file', csvFile);
      formData.append('proxy', campaignSettings.proxy || '');
      formData.append('haltOnCaptcha', campaignSettings.haltOnCaptcha ? 'true' : 'false');

      const startResponse = await api.post('/submissions/start', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (startResponse.data.success) {
        const actualCampaignId = startResponse.data.campaign_id;
        setCampaignId(actualCampaignId);
        setCampaignActive(true);
        
        toast.success('Campaign started successfully!', { id: toastId });
        
        // Start polling for progress
        startPollingProgress(actualCampaignId);
        
        // Set initial progress
        setRealTimeProgress({
          total: startResponse.data.total_urls,
          processed: 0,
          successful: 0,
          failed: 0,
          pending: startResponse.data.total_urls,
          progress_percent: 0,
          status: 'processing'
        });
      } else {
        throw new Error(startResponse.data.message || 'Failed to start campaign');
      }
      
    } catch (error) {
      console.error('Error creating campaign:', error);
      toast.error(error.response?.data?.detail || error.message || 'Failed to create campaign', { id: toastId });
      setCampaignActive(false);
    } finally {
      setSubmitting(false);
    }
  };

  const clearFile = () => {
    setCsvFile(null);
    setCsvPreview(null);
    setParseError(null);
    setUploadProgress(0);
    setCampaignName('');
    setCampaignMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getEstimatedTime = () => {
    if (!csvPreview) return null;
    const hours = Math.ceil(csvPreview.totalRows / 120);
    if (hours < 1) return "Less than 1 hour";
    if (hours < 24) return `~${hours} ${hours === 1 ? 'hour' : 'hours'}`;
    const days = Math.ceil(hours / 24);
    return `~${days} ${days === 1 ? 'day' : 'days'}`;
  };

  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "120 websites/hour",
      color: "from-yellow-400 to-orange-500"
    },
    {
      icon: Shield,
      title: "CAPTCHA Ready",
      description: "Auto-solving enabled",
      color: "from-blue-400 to-indigo-500"
    },
    {
      icon: Mail,
      title: "Email Fallback",
      description: "Never miss a contact",
      color: "from-green-400 to-emerald-500"
    },
    {
      icon: BarChart3,
      title: "Live Analytics",
      description: "Real-time tracking",
      color: "from-purple-400 to-pink-500"
    }
  ];

  const steps = [
    { 
      icon: Upload, 
      title: "Upload CSV", 
      description: "Add your website list",
      status: csvFile ? 'completed' : 'active'
    },
    { 
      icon: Settings, 
      title: "Configure", 
      description: "Set campaign options",
      status: csvFile ? (campaignName ? 'completed' : 'active') : 'pending'
    },
    { 
      icon: Play, 
      title: "Launch", 
      description: "Start processing",
      status: campaignActive ? 'completed' : 'pending'
    },
    { 
      icon: CheckCircle, 
      title: "Complete", 
      description: "Download results",
      status: realTimeProgress?.status === 'completed' ? 'completed' : 'pending'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/campaigns')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowRight className="w-5 h-5 rotate-180" />
              </button>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Create New Campaign
                </h1>
                <p className="text-gray-600 text-sm">Upload your CSV file to start automated outreach</p>
              </div>
            </div>
            
            {/* Logo */}
            <img 
              src="/assets/images/CPS_Header_Logo.png" 
              alt="Contact Page Submitter" 
              className="h-12"
            />
          </div>
        </div>
      </div>

      {/* Success Notification */}
      {campaignActive && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mr-4">
                <CheckCircle className="w-8 h-8" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-lg">Campaign Started Successfully!</p>
                <p className="text-green-100">Processing {realTimeProgress?.total || 0} websites...</p>
              </div>
              {realTimeProgress && (
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {Math.round(realTimeProgress.progress_percent || 0)}%
                  </div>
                  <div className="text-sm text-green-100">
                    {realTimeProgress.processed || 0} / {realTimeProgress.total || 0}
                  </div>
                </div>
              )}
            </div>
            
            {realTimeProgress && (
              <div className="mt-4">
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div 
                    className="bg-white h-2 rounded-full transition-all duration-300"
                    style={{ width: `${realTimeProgress.progress_percent || 0}%` }}
                  />
                </div>
                <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
                  <div>Success: {realTimeProgress.successful || 0}</div>
                  <div>Failed: {realTimeProgress.failed || 0}</div>
                  <div>Pending: {realTimeProgress.pending || 0}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-8 bg-white rounded-2xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              const isCompleted = step.status === 'completed';
              const isActive = step.status === 'active';
              const isPending = step.status === 'pending';
              
              return (
                <div key={idx} className="flex-1 flex items-center">
                  <div className="flex flex-col items-center relative">
                    <div className={`
                      w-14 h-14 rounded-2xl flex items-center justify-center transition-all
                      ${isCompleted ? 'bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg scale-110' :
                        isActive ? 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-md animate-pulse' :
                        'bg-gray-200'}
                    `}>
                      {isCompleted ? (
                        <Check className="w-7 h-7 text-white" />
                      ) : (
                        <Icon className={`w-7 h-7 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                      )}
                    </div>
                    <p className={`text-sm font-semibold mt-2 ${
                      isActive ? 'text-indigo-600' : isPending ? 'text-gray-400' : 'text-green-600'
                    }`}>
                      {step.title}
                    </p>
                    <p className="text-xs text-gray-500">{step.description}</p>
                  </div>
                  {idx < steps.length - 1 && (
                    <div className={`flex-1 h-1 mx-4 rounded-full transition-all ${
                      isCompleted ? 'bg-green-500' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div key={idx} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-all group cursor-pointer">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-500">{feature.description}</p>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* Upload Area */}
              <div className="p-8">
                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                  <FileSpreadsheet className="w-6 h-6 mr-2 text-indigo-600" />
                  Upload CSV File
                </h2>
                
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`relative rounded-2xl border-3 border-dashed transition-all cursor-pointer overflow-hidden ${
                    dragActive 
                      ? 'border-indigo-500 bg-gradient-to-br from-indigo-50 to-purple-50 scale-105' 
                      : csvFile 
                        ? 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50' 
                        : 'border-gray-300 bg-gradient-to-br from-gray-50 to-white hover:border-gray-400 hover:from-indigo-50 hover:to-purple-50'
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                    className="hidden"
                  />
                  
                  <div className="p-12 text-center">
                    {csvFile ? (
                      <>
                        <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                          <FileText className="w-10 h-10 text-white" />
                        </div>
                        <p className="text-xl font-bold text-gray-900">{csvFile.name}</p>
                        <p className="text-sm text-gray-500 mt-2">
                          Size: {(csvFile.size / 1024).toFixed(2)} KB • Websites: {csvPreview?.totalRows || 0}
                        </p>
                        
                        {/* Upload Progress */}
                        {uploadProgress > 0 && uploadProgress < 100 && (
                          <div className="mt-4">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all"
                                style={{ width: `${uploadProgress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{uploadProgress}% uploaded</p>
                          </div>
                        )}
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            clearFile();
                          }}
                          className="mt-4 px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium rounded-lg transition-colors inline-flex items-center"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Remove file
                        </button>
                      </>
                    ) : (
                      <>
                        <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <Upload className="w-10 h-10 text-indigo-600" />
                        </div>
                        <p className="text-xl font-semibold text-gray-900">
                          Drop your CSV file here
                        </p>
                        <p className="text-gray-500 mt-2">or click to browse</p>
                        <p className="text-sm text-gray-400 mt-4">
                          Supports CSV files up to 10MB
                        </p>
                      </>
                    )}
                  </div>
                </div>

                {/* Error Display */}
                {parseError && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
                    <div className="flex items-start">
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-3" />
                      <div>
                        <p className="font-semibold text-red-900">Error parsing CSV</p>
                        <p className="text-sm text-red-700 mt-1">{parseError}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* File Requirements */}
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <h3 className="text-sm font-bold text-blue-900 mb-3 flex items-center">
                    <Info className="w-4 h-4 mr-2" />
                    File Requirements
                  </h3>
                  <div className="space-y-2">
                    <div className="flex items-start text-sm text-blue-700">
                      <CheckCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-blue-600" />
                      <span>CSV format with 'website', 'url', 'domain', or 'site' column</span>
                    </div>
                    <div className="flex items-start text-sm text-blue-700">
                      <CheckCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-blue-600" />
                      <span>One URL per row (https://example.com)</span>
                    </div>
                    <div className="flex items-start text-sm text-blue-700">
                      <CheckCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-blue-600" />
                      <span>Maximum file size: 10MB (~50,000 URLs)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Campaign Settings & Preview */}
              {csvPreview && (
                <div className="p-8 border-t bg-gradient-to-br from-gray-50 to-white">
                  {/* Campaign Name */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Campaign Name *
                    </label>
                    <input
                      type="text"
                      value={campaignName}
                      onChange={(e) => setCampaignName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter campaign name..."
                    />
                  </div>

                  {/* Campaign Message */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Message Template
                    </label>
                    <textarea
                      value={campaignMessage}
                      onChange={(e) => setCampaignMessage(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Your message template for contact forms..."
                    />
                  </div>

                  {/* Settings */}
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Campaign Settings</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <label className="flex items-center p-3 bg-white rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50">
                        <input
                          type="checkbox"
                          checked={campaignSettings.emailFallback}
                          onChange={(e) => setCampaignSettings({...campaignSettings, emailFallback: e.target.checked})}
                          className="w-4 h-4 text-indigo-600 rounded"
                        />
                        <span className="ml-3 text-sm">Use email fallback</span>
                      </label>
                      
                      <label className="flex items-center p-3 bg-white rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50">
                        <input
                          type="checkbox"
                          checked={campaignSettings.captchaHandling}
                          onChange={(e) => setCampaignSettings({...campaignSettings, captchaHandling: e.target.checked})}
                          className="w-4 h-4 text-indigo-600 rounded"
                        />
                        <span className="ml-3 text-sm">Auto-solve CAPTCHAs</span>
                      </label>
                      
                      <div className="col-span-full">
                        <label className="block text-sm text-gray-700 mb-2">Proxy (optional)</label>
                        <input
                          type="text"
                          value={campaignSettings.proxy}
                          onChange={(e) => setCampaignSettings({...campaignSettings, proxy: e.target.value})}
                          placeholder="http://proxy:port or leave empty"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Preview */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
                  <div className="border border-gray-200 rounded-xl overflow-hidden bg-white">
                    <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-3">
                      <p className="text-white font-semibold">
                        {csvPreview.websiteColumnName} ({csvPreview.totalRows} total websites)
                      </p>
                    </div>
                    <div className="max-h-60 overflow-y-auto">
                      {csvPreview.rows.map((row, idx) => (
                        <div key={idx} className="flex items-center px-4 py-3 border-b hover:bg-gray-50 transition-colors">
                          <Globe className="w-4 h-4 text-gray-400 mr-3" />
                          <span className="text-sm font-medium text-gray-700">
                            {row[csvPreview.websiteColumnIndex]}
                          </span>
                        </div>
                      ))}
                      {csvPreview.totalRows > csvPreview.rows.length && (
                        <div className="px-4 py-3 bg-gray-50 text-center">
                          <p className="text-sm text-gray-500 italic">
                            ... and {csvPreview.totalRows - csvPreview.rows.length} more websites
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-8 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">
                        Estimated processing time: 
                        <span className="font-bold text-gray-900 ml-2 text-lg">{getEstimatedTime()}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Processing speed: ~120 websites per hour
                      </p>
                    </div>
                    <button
                      onClick={handleSubmit}
                      disabled={submitting || !campaignName.trim() || campaignActive}
                      className={`px-8 py-4 rounded-xl font-bold text-lg transition-all flex items-center shadow-lg hover:shadow-xl transform hover:scale-105 ${
                        submitting || !campaignName.trim() || campaignActive
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                      }`}
                    >
                      {submitting ? (
                        <>
                          <Loader className="w-6 h-6 animate-spin mr-3" />
                          Creating Campaign...
                        </>
                      ) : campaignActive ? (
                        <>
                          <Activity className="w-6 h-6 mr-3" />
                          Campaign Running...
                        </>
                      ) : (
                        <>
                          <Rocket className="w-6 h-6 mr-3" />
                          Launch Campaign
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Real-time Progress */}
            {realTimeProgress && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                  Live Progress
                </h3>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-indigo-600">
                      {Math.round(realTimeProgress.progress_percent || 0)}%
                    </div>
                    <div className="text-sm text-gray-600">Complete</div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${realTimeProgress.progress_percent || 0}%` }}
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-green-50 p-2 rounded text-center">
                      <div className="font-bold text-green-600">{realTimeProgress.successful || 0}</div>
                      <div className="text-green-700">Success</div>
                    </div>
                    <div className="bg-red-50 p-2 rounded text-center">
                      <div className="font-bold text-red-600">{realTimeProgress.failed || 0}</div>
                      <div className="text-red-700">Failed</div>
                    </div>
                  </div>
                  
                  <div className="text-center text-sm text-gray-600">
                    {realTimeProgress.processed || 0} of {realTimeProgress.total || 0} processed
                  </div>
                </div>
              </div>
            )}

            {/* Performance Card */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                Performance Metrics
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center mr-3">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">Success Rate</p>
                      <p className="text-xs text-gray-500">Forms found & filled</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-green-600">97%</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                      <Zap className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">Processing Speed</p>
                      <p className="text-xs text-gray-500">Websites per hour</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-blue-600">120</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center mr-3">
                      <Mail className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">Email Fallback</p>
                      <p className="text-xs text-gray-500">When no form found</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-purple-600">100%</span>
                </div>
              </div>
            </div>

            {/* How It Works */}
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                How It Works
              </h3>
              <div className="space-y-3">
                {[
                  { text: "AI finds contact forms on each website", icon: Target },
                  { text: "Your info is filled automatically", icon: Cpu },
                  { text: "CAPTCHAs are solved in real-time", icon: Shield },
                  { text: "Email used if no form is found", icon: Mail },
                  { text: "Track progress on dashboard", icon: Activity }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <item.icon className="w-4 h-4" />
                    </div>
                    <p className="text-sm ml-3 text-white/90">{item.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Important Notes */}
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-6">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="ml-3">
                  <p className="text-sm font-bold text-amber-900">Important Notes</p>
                  <ul className="text-xs text-amber-700 mt-2 space-y-1">
                    <li>• Only one campaign runs at a time</li>
                    <li>• Large files (10K+ URLs) take 3-4 days</li>
                    <li>• Check dashboard for live updates</li>
                    <li>• Download results when complete</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormSubmitterPage;