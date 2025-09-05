// src/pages/FormSubmitterPage.jsx - Fixed CSV Reading
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, FileText, CheckCircle, Loader, X, AlertCircle, 
  ArrowRight, Clock, Globe, Mail, Zap, Target, Activity,
  ChevronRight, Database, Shield, TrendingUp
} from 'lucide-react';

const FormSubmitterPage = () => {
  const navigate = useNavigate();
  const [csvFile, setCsvFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [csvPreview, setCsvPreview] = useState(null);
  const [campaignActive, setCampaignActive] = useState(false);
  const [parseError, setParseError] = useState(null);
  const fileInputRef = useRef(null);

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
      h.toLowerCase().includes('domain')
    );

    if (websiteIndex === -1) {
      throw new Error("CSV must contain a 'website', 'url', or 'domain' column");
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
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      setParseError('File size must be less than 10MB');
      return;
    }
    
    setParseError(null);
    setCsvFile(file);
    
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
      
    } catch (error) {
      console.error('Error parsing CSV:', error);
      setParseError(error.message || 'Failed to parse CSV file');
      setCsvFile(null);
      setCsvPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!csvFile) {
      alert('Please select a CSV file');
      return;
    }
    
    setSubmitting(true);
    
    // Simulate API call
    setTimeout(() => {
      setSubmitting(false);
      setCampaignActive(true);
      // Redirect to dashboard after starting
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    }, 2000);
  };

  const clearFile = () => {
    setCsvFile(null);
    setCsvPreview(null);
    setParseError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getEstimatedTime = () => {
    if (!csvPreview) return null;
    const hours = Math.ceil(csvPreview.totalRows / 120);
    if (hours < 1) return "Less than 1 hour";
    return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
  };

  const stats = [
    { icon: Zap, label: "Processing Speed", value: "120/hour", color: "text-yellow-600" },
    { icon: Target, label: "Success Rate", value: "97%", color: "text-green-600" },
    { icon: Mail, label: "Email Fallback", value: "Enabled", color: "text-blue-600" },
    { icon: Shield, label: "CAPTCHA Solving", value: "Active", color: "text-purple-600" }
  ];

  const steps = [
    { title: "Upload CSV", description: "Add your website list" },
    { title: "Validation", description: "We verify your data" },
    { title: "Processing", description: "Forms are submitted" },
    { title: "Complete", description: "Download report" }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Start New Campaign</h1>
              <p className="text-gray-600 mt-1">Upload your CSV file to begin automated outreach</p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Success Notification */}
      {campaignActive && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
              <div className="flex-1">
                <p className="font-semibold text-green-900">Campaign Started Successfully!</p>
                <p className="text-sm text-green-700">Redirecting to dashboard...</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, idx) => (
              <div key={idx} className="flex-1 flex items-center">
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    idx === 0 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {idx + 1}
                  </div>
                  <p className="text-sm font-medium text-gray-900 mt-2">{step.title}</p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
                {idx < steps.length - 1 && (
                  <ChevronRight className="w-5 h-5 text-gray-300 mx-4 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              {/* Upload Area */}
              <div className="p-8">
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`relative rounded-lg border-2 border-dashed transition-all cursor-pointer ${
                    dragActive 
                      ? 'border-indigo-500 bg-indigo-50' 
                      : csvFile 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-300 bg-gray-50 hover:border-gray-400'
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                    className="hidden"
                  />
                  
                  <div className="p-8 text-center">
                    {csvFile ? (
                      <>
                        <FileText className="w-16 h-16 text-green-600 mx-auto mb-4" />
                        <p className="text-lg font-semibold text-gray-900">{csvFile.name}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {(csvFile.size / 1024).toFixed(2)} KB • {csvPreview?.totalRows || 0} websites
                        </p>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            clearFile();
                          }}
                          className="mt-4 text-sm text-red-600 hover:text-red-700 font-medium flex items-center mx-auto"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Remove file
                        </button>
                      </>
                    ) : (
                      <>
                        <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-lg font-medium text-gray-900">
                          Drop your CSV file here, or click to browse
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                          Supports CSV files up to 10MB
                        </p>
                      </>
                    )}
                  </div>
                </div>

                {/* Error Display */}
                {parseError && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center">
                      <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
                      <div>
                        <p className="font-semibold text-red-900">Error parsing CSV</p>
                        <p className="text-sm text-red-700">{parseError}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* File Requirements */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-sm font-semibold text-blue-900 mb-2">File Requirements</h3>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li className="flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      CSV format with 'website', 'url', or 'domain' column
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      One URL per row (https://example.com)
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Maximum file size: 10MB
                    </li>
                  </ul>
                </div>
              </div>

              {/* Preview Section */}
              {csvPreview && (
                <div className="p-8 border-t">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                            {csvPreview.websiteColumnName} ({csvPreview.totalRows} total)
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {csvPreview.rows.map((row, idx) => (
                          <tr key={idx}>
                            <td className="px-4 py-3 text-sm text-gray-600">
                              <Globe className="w-4 h-4 inline mr-2 text-gray-400" />
                              {row[csvPreview.websiteColumnIndex]}
                            </td>
                          </tr>
                        ))}
                        {csvPreview.totalRows > csvPreview.rows.length && (
                          <tr className="bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-500 italic">
                              ... and {csvPreview.totalRows - csvPreview.rows.length} more websites
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-6 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">
                        Estimated processing time: 
                        <span className="font-semibold text-gray-900 ml-1">{getEstimatedTime()}</span>
                      </p>
                    </div>
                    <button
                      onClick={handleSubmit}
                      disabled={submitting}
                      className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center ${
                        submitting
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      }`}
                    >
                      {submitting ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin mr-2" />
                          Starting Campaign...
                        </>
                      ) : (
                        <>
                          Start Campaign
                          <ArrowRight className="w-5 h-5 ml-2" />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar - Same as before */}
          <div className="lg:col-span-1 space-y-6">
            {/* Stats Grid */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                {stats.map((stat, idx) => {
                  const Icon = stat.icon;
                  return (
                    <div key={idx} className="text-center">
                      <Icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
                      <p className="text-xl font-bold text-gray-900">{stat.value}</p>
                      <p className="text-xs text-gray-500">{stat.label}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* How It Works */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">How It Works</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-indigo-600">1</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Automatic Form Detection</p>
                    <p className="text-xs text-gray-500">We find contact forms on each website</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-indigo-600">2</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Smart Field Mapping</p>
                    <p className="text-xs text-gray-500">Your info is filled accurately</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-indigo-600">3</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Email Fallback</p>
                    <p className="text-xs text-gray-500">Uses email if no form found</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-indigo-600">4</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Real-time Tracking</p>
                    <p className="text-xs text-gray-500">Monitor progress on dashboard</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Important Notes */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="ml-3">
                  <p className="text-sm font-semibold text-amber-900">Important Notes</p>
                  <ul className="text-xs text-amber-700 mt-2 space-y-1">
                    <li>• Only one campaign can run at a time</li>
                    <li>• Campaign runs until all sites are processed</li>
                    <li>• Average processing: 120 websites/hour</li>
                    <li>• Check dashboard for live updates</li>
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