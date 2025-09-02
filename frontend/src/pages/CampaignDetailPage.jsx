// src/pages/CampaignDetailPage.jsx
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, Play, CheckCircle, XCircle, Clock, Mail, Globe, 
  AlertCircle, FileText, TrendingUp, Download, RefreshCw,
  Activity, Target, BarChart3, Eye, Send, AlertTriangle,
  Calendar, Hash, Pause, X
} from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

const CampaignDetailPage = () => {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchCampaignDetails();
    
    // Auto-refresh if campaign is running
    const interval = setInterval(() => {
      if (campaign?.status === 'running') {
        fetchCampaignDetails(true);
      }
    }, 3000); // Refresh every 3 seconds

    return () => clearInterval(interval);
  }, [campaignId, campaign?.status]);

  const fetchCampaignDetails = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      else setRefreshing(true);
      
      const [campaignRes, logsRes] = await Promise.all([
        api.get(`/campaigns/${campaignId}`),
        api.get(`/campaigns/${campaignId}/logs?limit=50`)
      ]);
      
      setCampaign(campaignRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error('Error fetching campaign details:', error);
      toast.error('Failed to load campaign details');
      navigate('/dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleStopCampaign = async () => {
    if (!window.confirm('Are you sure you want to stop this campaign?')) return;
    
    try {
      await api.post(`/campaigns/${campaignId}/stop`);
      toast.success('Campaign stopped');
      fetchCampaignDetails();
    } catch (error) {
      toast.error('Failed to stop campaign');
    }
  };

  const handleDownloadReport = async () => {
    try {
      const response = await api.get(`/campaigns/${campaignId}/export`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `campaign-${campaignId}-report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'stopped': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'email_fallback': return <Mail className="w-4 h-4 text-blue-600" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'no_form': return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      default: return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = Math.floor((end - start) / 1000); // seconds
    
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    const seconds = diff % 60;
    
    if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
    if (minutes > 0) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading campaign details...</p>
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Campaign not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const successRate = Math.round((campaign.successful / Math.max(campaign.processed, 1)) * 100);
  const isRunning = campaign.status === 'running';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {campaign.name || `Campaign #${campaign.id}`}
                </h1>
                <p className="text-gray-600">
                  {campaign.fileName} • Started {new Date(campaign.startTime).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {refreshing && (
                <div className="flex items-center text-sm text-gray-500">
                  <RefreshCw className="w-4 h-4 animate-spin mr-1" />
                  Updating...
                </div>
              )}
              
              {isRunning && (
                <button
                  onClick={handleStopCampaign}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
                >
                  <X className="w-4 h-4" />
                  <span>Stop Campaign</span>
                </button>
              )}
              
              {campaign.status === 'completed' && (
                <button
                  onClick={handleDownloadReport}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Report</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Status Card */}
        <div className={`rounded-xl shadow-lg border-2 p-6 mb-6 ${
          isRunning ? 'bg-green-50 border-green-500' : 
          campaign.status === 'completed' ? 'bg-blue-50 border-blue-500' :
          'bg-gray-50 border-gray-500'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isRunning ? 'bg-green-100' : 
                campaign.status === 'completed' ? 'bg-blue-100' :
                'bg-gray-100'
              }`}>
                {isRunning ? (
                  <Play className="w-6 h-6 text-green-600" />
                ) : campaign.status === 'completed' ? (
                  <CheckCircle className="w-6 h-6 text-blue-600" />
                ) : (
                  <Pause className="w-6 h-6 text-gray-600" />
                )}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-xl font-bold text-gray-900">
                    Campaign {campaign.status === 'running' ? 'Running' : 
                             campaign.status === 'completed' ? 'Completed' : 
                             'Stopped'}
                  </h2>
                  {isRunning && (
                    <div className="flex items-center space-x-1 text-sm text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>Live</span>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  Duration: {formatDuration(campaign.startTime, campaign.endTime)}
                </p>
              </div>
            </div>
            
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">{successRate}%</p>
              <p className="text-sm text-gray-600">Success Rate</p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-700 font-medium">
                {campaign.processed} of {campaign.totalWebsites} websites processed
              </span>
              <span className="font-bold text-gray-900">
                {Math.round((campaign.processed / campaign.totalWebsites) * 100)}%
              </span>
            </div>
            <div className="w-full bg-white rounded-full h-6 shadow-inner">
              <div 
                className={`h-6 rounded-full transition-all duration-500 ${
                  isRunning ? 'bg-gradient-to-r from-green-500 to-green-600' :
                  campaign.status === 'completed' ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                  'bg-gray-500'
                }`}
                style={{ width: `${(campaign.processed / campaign.totalWebsites) * 100}%` }}
              />
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-gray-900">{campaign.totalWebsites}</p>
              <p className="text-xs text-gray-600">Total Sites</p>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-green-600">{campaign.successful}</p>
              <p className="text-xs text-gray-600">Successful</p>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-blue-600">{campaign.emailFallback || 0}</p>
              <p className="text-xs text-gray-600">Email Sent</p>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-yellow-600">{campaign.noForm || 0}</p>
              <p className="text-xs text-gray-600">No Form</p>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-600">{campaign.failed}</p>
              <p className="text-xs text-gray-600">Failed</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg border overflow-hidden">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'overview' 
                    ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`px-6 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'logs' 
                    ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Activity Logs ({logs.length})
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-6 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'analytics' 
                    ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Analytics
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Information</h3>
                    <dl className="space-y-3">
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-600">Campaign ID</dt>
                        <dd className="text-sm font-medium text-gray-900">#{campaign.id}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-600">File Name</dt>
                        <dd className="text-sm font-medium text-gray-900">{campaign.fileName}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-600">Started</dt>
                        <dd className="text-sm font-medium text-gray-900">
                          {new Date(campaign.startTime).toLocaleString()}
                        </dd>
                      </div>
                      {campaign.endTime && (
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-600">Ended</dt>
                          <dd className="text-sm font-medium text-gray-900">
                            {new Date(campaign.endTime).toLocaleString()}
                          </dd>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-600">Processing Rate</dt>
                        <dd className="text-sm font-medium text-gray-900">~120 sites/hour</dd>
                      </div>
                    </dl>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">Form Success</span>
                          <span className="font-medium text-gray-900">
                            {Math.round((campaign.successful / Math.max(campaign.processed, 1)) * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${(campaign.successful / Math.max(campaign.processed, 1)) * 100}%` }}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">Email Fallback</span>
                          <span className="font-medium text-gray-900">
                            {Math.round(((campaign.emailFallback || 0) / Math.max(campaign.processed, 1)) * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${((campaign.emailFallback || 0) / Math.max(campaign.processed, 1)) * 100}%` }}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">Failed</span>
                          <span className="font-medium text-gray-900">
                            {Math.round((campaign.failed / Math.max(campaign.processed, 1)) * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-500 h-2 rounded-full"
                            style={{ width: `${(campaign.failed / Math.max(campaign.processed, 1)) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Message Template */}
                {campaign.messageTemplate && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Template Used</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {campaign.messageTemplate}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Logs Tab */}
            {activeTab === 'logs' && (
              <div className="space-y-4">
                {logs.length > 0 ? (
                  <div className="space-y-2">
                    {logs.map((log, idx) => (
                      <div key={idx} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                        {getLogIcon(log.type)}
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            {log.website}
                          </p>
                          <p className="text-xs text-gray-500">
                            {log.message} • {new Date(log.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                        <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                          log.type === 'success' ? 'bg-green-100 text-green-800' :
                          log.type === 'email_fallback' ? 'bg-blue-100 text-blue-800' :
                          log.type === 'no_form' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {log.type.replace('_', ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Activity className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No activity logs yet</p>
                    <p className="text-sm text-gray-400 mt-1">Logs will appear as the campaign processes websites</p>
                  </div>
                )}
              </div>
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Target className="w-8 h-8 text-green-600" />
                      <span className="text-2xl font-bold text-green-700">{successRate}%</span>
                    </div>
                    <p className="text-sm font-medium text-green-800">Overall Success Rate</p>
                    <p className="text-xs text-green-600 mt-1">Above average performance</p>
                  </div>
                  
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Clock className="w-8 h-8 text-blue-600" />
                      <span className="text-2xl font-bold text-blue-700">
                        {Math.round(campaign.processed / (campaign.duration || 1))} /hr
                      </span>
                    </div>
                    <p className="text-sm font-medium text-blue-800">Processing Speed</p>
                    <p className="text-xs text-blue-600 mt-1">Sites per hour</p>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Send className="w-8 h-8 text-purple-600" />
                      <span className="text-2xl font-bold text-purple-700">
                        {campaign.successful + (campaign.emailFallback || 0)}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-purple-800">Messages Delivered</p>
                    <p className="text-xs text-purple-600 mt-1">Total outreach</p>
                  </div>
                </div>

                {/* Failure Analysis */}
                {campaign.failed > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Failure Analysis</h3>
                    <div className="bg-red-50 rounded-lg p-4">
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-700">CAPTCHA Failures</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.captchaFailed || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-700">No Contact Form Found</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.noForm || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-700">Website Unreachable</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.unreachable || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-700">Other Errors</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.failed - (campaign.captchaFailed || 0) - (campaign.noForm || 0) - (campaign.unreachable || 0)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CampaignDetailPage;