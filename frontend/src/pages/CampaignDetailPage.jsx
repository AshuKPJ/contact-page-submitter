// src/pages/CampaignDetailPage.jsx
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, Play, CheckCircle, XCircle, Clock, Mail, Globe, 
  AlertCircle, FileText, TrendingUp, Download, RefreshCw,
  Activity, Target, BarChart3, Eye, Send, AlertTriangle,
  Calendar, Hash, Pause, X, Shield, Database
} from "lucide-react";
import api from "../services/api";
import { toast } from "react-hot-toast";
import { trackEvent } from "../services/telemetry";

const CampaignDetailPage = () => {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState(null);
  const [logs, setLogs] = useState([]);
  const [submissionLogs, setSubmissionLogs] = useState([]);
  const [websites, setWebsites] = useState([]);
  const [captchaStats, setCaptchaStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  // Safety check: if campaignId is "new", redirect to FormSubmitterPage
  useEffect(() => {
    if (campaignId === 'new') {
      console.log('[CAMPAIGN_DETAIL] Detected "new" as campaignId, redirecting to form submitter');
      navigate('/form-submitter', { replace: true });
      return;
    }
  }, [campaignId, navigate]);

  // Main data fetching effect
  useEffect(() => {
    if (!campaignId || campaignId === 'new') return;

    const fetchDetails = async (silent = false) => {
      try {
        if (!silent) setLoading(true);
        else setRefreshing(true);
        
        console.log(`[CAMPAIGN_DETAIL] Fetching details for campaign: ${campaignId}`);
        
        // Fetch all campaign data in parallel
        const [campaignRes, logsRes, submissionLogsRes, websitesRes, captchaRes] = await Promise.allSettled([
          api.get(`/campaigns/${campaignId}`),
          api.get(`/campaigns/${campaignId}/logs`),
          api.get(`/submission-logs?campaign_id=${campaignId}`),
          api.get(`/campaigns/${campaignId}/websites`),
          api.get(`/captcha/stats?campaign_id=${campaignId}`)
        ]);
        
        // Process campaign data
        if (campaignRes.status === 'fulfilled') {
          setCampaign(campaignRes.value.data);
        }
        
        // Process logs
        if (logsRes.status === 'fulfilled') {
          setLogs(logsRes.value.data || []);
        }
        
        // Process submission logs
        if (submissionLogsRes.status === 'fulfilled') {
          setSubmissionLogs(submissionLogsRes.value.data || []);
        }
        
        // Process websites
        if (websitesRes.status === 'fulfilled') {
          setWebsites(websitesRes.value.data || []);
        }
        
        // Process CAPTCHA stats
        if (captchaRes.status === 'fulfilled') {
          setCaptchaStats(captchaRes.value.data);
        }
        
        // Log automation progress
        if (campaignRes.status === 'fulfilled') {
          const campaignData = campaignRes.value.data;
          console.log('[AUTOMATION PROGRESS]', {
            status: campaignData.status,
            processed: campaignData.processed || 0,
            total: campaignData.totalWebsites || 0,
            successful: campaignData.successful || 0,
            failed: campaignData.failed || 0,
            percentComplete: campaignData.totalWebsites > 0 
              ? Math.round((campaignData.processed / campaignData.totalWebsites) * 100)
              : 0
          });
          
          // Track campaign view
          await trackEvent({
            level: 'INFO',
            message: 'Campaign viewed',
            campaign_id: campaignId,
            context: { status: campaignData.status }
          });
        }
        
      } catch (error) {
        console.error('[CAMPAIGN_DETAIL] Error fetching campaign details:', error);
        
        if (!silent) {
          if (error.response?.status === 404) {
            toast.error(`Campaign not found`);
            navigate('/campaigns');
          } else {
            toast.error('Failed to load campaign details');
          }
          
          await trackEvent({
            level: 'ERROR',
            message: 'Failed to load campaign details',
            campaign_id: campaignId,
            context: { error: error.message }
          });
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    };

    // Initial fetch
    fetchDetails(false);

    // Set up auto-refresh interval
    const interval = setInterval(() => {
      // Only refresh if document is visible and campaign might be active
      if (document.visibilityState === 'visible') {
        fetchDetails(true); // Silent refresh
      }
    }, 2000); // Refresh every 2 seconds

    return () => clearInterval(interval);
  }, [campaignId, navigate]);

  const handleStopCampaign = async () => {
    if (!window.confirm('Are you sure you want to stop this campaign?')) return;
    
    try {
      await api.post(`/campaigns/${campaignId}/stop`);
      toast.success('Campaign stopped');
      
      await trackEvent({
        level: 'INFO',
        message: 'Campaign stopped',
        campaign_id: campaignId
      });
      
      // Refresh campaign details
      const response = await api.get(`/campaigns/${campaignId}`);
      setCampaign(response.data);
    } catch (error) {
      console.error('[CAMPAIGN_DETAIL] Error stopping campaign:', error);
      toast.error('Failed to stop campaign');
      
      await trackEvent({
        level: 'ERROR',
        message: 'Failed to stop campaign',
        campaign_id: campaignId,
        context: { error: error.message }
      });
    }
  };

  const handleStartCampaign = async () => {
    try {
      await api.post(`/campaigns/${campaignId}/start`);
      toast.success('Campaign started! Processing will begin shortly...');
      
      await trackEvent({
        level: 'INFO',
        message: 'Campaign started',
        campaign_id: campaignId
      });
      
      // Refresh campaign details
      const response = await api.get(`/campaigns/${campaignId}`);
      setCampaign(response.data);
    } catch (error) {
      console.error('[CAMPAIGN_DETAIL] Error starting campaign:', error);
      toast.error(error.response?.data?.detail || 'Failed to start campaign');
      
      await trackEvent({
        level: 'ERROR',
        message: 'Failed to start campaign',
        campaign_id: campaignId,
        context: { error: error.message }
      });
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
      
      await trackEvent({
        level: 'INFO',
        message: 'Campaign report downloaded',
        campaign_id: campaignId
      });
    } catch (error) {
      toast.error('Failed to download report');
      
      await trackEvent({
        level: 'ERROR',
        message: 'Failed to download report',
        campaign_id: campaignId,
        context: { error: error.message }
      });
    }
  };

  const getStatusColor = (status) => {
    const statusStr = status?.toString().toLowerCase();
    switch (statusStr) {
      case 'active':
      case 'running':
        return 'bg-green-100 text-green-700';
      case 'completed':
        return 'bg-blue-100 text-blue-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'paused':
        return 'bg-yellow-100 text-yellow-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDuration = (startTime, endTime) => {
    if (!startTime) return 'N/A';
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = Math.floor((end - start) / 1000);
    
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  // Don't render if campaignId is "new"
  if (campaignId === 'new') {
    return null;
  }

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
            onClick={() => navigate('/campaigns')}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Back to Campaigns
          </button>
        </div>
      </div>
    );
  }

  const successRate = Math.round((campaign.successful / Math.max(campaign.processed, 1)) * 100);
  const isRunning = campaign.status === 'ACTIVE' || campaign.status === 'running';
  const isDraft = campaign.status === 'DRAFT' || campaign.status === 'draft';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Show automation status banner */}
      {isRunning && (
        <div className="bg-green-500 text-white px-4 py-2">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span className="font-medium">Automation Running</span>
              <span className="text-green-100">
                Processing website {campaign.processed + 1} of {campaign.totalWebsites}
              </span>
            </div>
            <span className="text-sm">
              ~{Math.ceil((campaign.totalWebsites - campaign.processed) / 120)} hours remaining
            </span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/campaigns')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {campaign.name || `Campaign #${campaign.id}`}
                </h1>
                <p className="text-gray-600">
                  {campaign.fileName || campaign.file_name} • 
                  {campaign.totalWebsites || campaign.total_websites || 0} URLs
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
              
              {isDraft && (
                <button
                  onClick={handleStartCampaign}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Start Campaign</span>
                </button>
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
              
              {campaign.status === 'COMPLETED' && (
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

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {['overview', 'submissions', 'websites', 'logs'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                    activeTab === tab
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">Total URLs</span>
                      <Globe className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {campaign.totalWebsites || campaign.total_websites || 0}
                    </p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">Processed</span>
                      <Activity className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {campaign.processed || 0}
                    </p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">Success Rate</span>
                      <Target className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {successRate}%
                    </p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">Duration</span>
                      <Clock className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatDuration(campaign.started_at, campaign.completed_at)}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>{Math.round((campaign.processed / Math.max(campaign.totalWebsites, 1)) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-indigo-600 h-3 rounded-full transition-all"
                      style={{ width: `${Math.round((campaign.processed / Math.max(campaign.totalWebsites, 1)) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* CAPTCHA Stats */}
                {captchaStats && (
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <Shield className="w-5 h-5 text-blue-600 mr-2" />
                      <h3 className="font-semibold text-gray-900">CAPTCHA Statistics</h3>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Encountered:</span>
                        <p className="font-semibold text-gray-900">{captchaStats.encountered || 0}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Solved:</span>
                        <p className="font-semibold text-gray-900">{captchaStats.solved || 0}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Success Rate:</span>
                        <p className="font-semibold text-gray-900">
                          {captchaStats.success_rate || 0}%
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'submissions' && (
              <div className="space-y-4">
                {submissionLogs.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            URL
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Timestamp
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Details
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {submissionLogs.map((log) => (
                          <tr key={log.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {log.target_url}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                log.status === 'success' ? 'bg-green-100 text-green-800' :
                                log.status === 'failed' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {log.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(log.timestamp).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {log.details}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No submission logs available</p>
                )}
              </div>
            )}

            {activeTab === 'websites' && (
              <div className="space-y-4">
                {websites.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Domain
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Form Detected
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            CAPTCHA
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {websites.map((website) => (
                          <tr key={website.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {website.domain}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {website.form_detected ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-500" />
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {website.has_captcha ? website.captcha_type : 'None'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(website.status)}`}>
                                {website.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No website data available</p>
                )}
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="space-y-4">
                {logs.length > 0 ? (
                  <div className="space-y-2">
                    {logs.map((log, idx) => (
                      <div key={idx} className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{log.action}</p>
                            <p className="text-xs text-gray-500 mt-1">{log.details}</p>
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No logs available</p>
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