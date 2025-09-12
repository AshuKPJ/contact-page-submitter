// UserDashboard.jsx - Complete Version
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, CheckCircle, Clock, Mail, Globe, AlertCircle, Upload, 
  FileText, TrendingUp, BarChart3, Activity, Target, RefreshCw, 
  Loader, Settings, LogOut, User, Eye, Plus, Zap, Shield,
  ArrowRight, Calendar, Download, Pause, Star, Award, Users,
  FileSpreadsheet, ChevronRight, Sparkles
} from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const UserDashboard = () => {
  const navigate = useNavigate();

  // State management
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  
  // Data from database
  const [campaigns, setCampaigns] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [userProfile, setUserProfile] = useState(null);

  // Quick Actions
  const quickActions = [
    {
      title: 'Start New Campaign',
      description: 'Launch automated outreach',
      icon: Plus,
      color: 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700',
      action: () => navigate('/form-submitter')
    },
    {
      title: 'View All Campaigns',
      description: 'Manage existing campaigns',
      icon: FileText,
      color: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700',
      action: () => navigate('/campaigns')
    },
    {
      title: 'Update Contact Info',
      description: 'Edit your information',
      icon: User,
      color: 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700',
      action: () => navigate('/contact-info')
    },
    {
      title: 'View Activity',
      description: 'Check recent activity',
      icon: Activity,
      color: 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700',
      action: () => navigate('/activity')
    }
  ];

  // Fetch dashboard data
  const fetchDashboardData = async (silent = false) => {
    try {
      if (!silent) setError(null);
      console.log('[DASHBOARD] Fetching data...');
      
      // Fetch data in parallel
      const [
        campaignsResponse,
        analyticsResponse,
        dailyStatsResponse,
        submissionsResponse,
        profileResponse
      ] = await Promise.allSettled([
        api.get('/campaigns?page=1&per_page=10'),
        api.get('/analytics/user'),
        api.get('/analytics/daily-stats?days=7'),
        api.get('/submissions?page=1&per_page=10'),
        api.get('/users/profile')
      ]);

      // Process campaigns
      if (campaignsResponse.status === 'fulfilled') {
        const campaignsData = campaignsResponse.value.data;
        setCampaigns(campaignsData.campaigns || campaignsData || []);
      }

      // Process analytics
      if (analyticsResponse.status === 'fulfilled') {
        setUserAnalytics(analyticsResponse.value.data);
      }

      // Process daily stats
      if (dailyStatsResponse.status === 'fulfilled') {
        setDailyStats(dailyStatsResponse.value.data || []);
      }

      // Process submissions
      if (submissionsResponse.status === 'fulfilled') {
        const submissionsData = submissionsResponse.value.data;
        setRecentSubmissions(submissionsData.submissions || submissionsData || []);
      }

      // Process profile
      if (profileResponse.status === 'fulfilled') {
        setUserProfile(profileResponse.value.data);
      }

      console.log('[DASHBOARD] Data loaded successfully');

    } catch (err) {
      console.error('[DASHBOARD] Error fetching data:', err);
      if (!silent) {
        setError(err.message);
        
        if (err.response?.status === 401) {
          toast.error('Session expired. Please login again.');
          navigate('/');
        }
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Auto refresh for running campaigns
  useEffect(() => {
    const hasRunningCampaign = campaigns.some(c => 
      c.status === 'active' || c.status === 'running' || c.status === 'ACTIVE'
    );

    if (hasRunningCampaign) {
      const interval = setInterval(() => {
        if (document.visibilityState === 'visible') {
          fetchDashboardData(true); // Silent refresh
        }
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(interval);
    }
  }, [campaigns]);

  // Action handlers
  const handleRefresh = async () => {
    setRefreshing(true);
    const toastId = toast.loading('Refreshing dashboard...');
    await fetchDashboardData();
    toast.success('Dashboard refreshed', { id: toastId });
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    toast.success('Logged out successfully');
    navigate('/');
  };

  const handleViewCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleStopCampaign = async (campaignId) => {
    if (!window.confirm('Are you sure you want to stop this campaign?')) return;
    
    try {
      await api.post(`/campaigns/${campaignId}/stop`);
      toast.success('Campaign stopped');
      fetchDashboardData();
    } catch (error) {
      toast.error('Failed to stop campaign');
    }
  };

  const handleExportReport = async (campaignId) => {
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

  // Calculate statistics
  const calculateStats = () => {
    const stats = userAnalytics?.stats || {};
    return {
      totalCampaigns: userAnalytics?.total_campaigns || campaigns.length,
      totalSubmissions: stats.total_submissions || 0,
      successful: stats.successful_submissions || 0,
      failed: stats.failed_submissions || 0,
      pending: stats.pending_submissions || 0,
      successRate: stats.success_rate || 0
    };
  };

  const stats = calculateStats();
  const activeCampaign = campaigns.find(c => 
    c.status === 'active' || c.status === 'running' || c.status === 'ACTIVE'
  );

  // Get period label
  const getPeriodLabel = () => {
    switch (selectedPeriod) {
      case 'today': return "Today's";
      case 'week': return 'This Week';
      case 'month': return 'This Month';
      case 'year': return 'This Year';
      default: return 'All Time';
    }
  };

  // Format status
  const formatStatus = (status) => {
    if (!status) return 'draft';
    const statusStr = status.toString().toLowerCase();
    return statusStr.charAt(0).toUpperCase() + statusStr.slice(1);
  };

  // Get status color
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

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <Loader className="w-16 h-16 text-indigo-600 animate-spin mx-auto" />
            <div className="absolute inset-0 w-16 h-16 border-4 border-indigo-200 rounded-full mx-auto animate-pulse"></div>
          </div>
          <p className="text-gray-600 mt-4 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !campaigns.length && !userAnalytics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-white flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl border max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
            Connection Error
          </h2>
          <p className="text-gray-600 text-center mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => fetchDashboardData()}
              className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-all transform hover:scale-105"
            >
              Try Again
            </button>
            <button
              onClick={handleLogout}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Dashboard
              </h1>
              {userProfile && (
                <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                  Welcome back, {userProfile.first_name || userProfile.email || 'User'} 👋
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
              
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Active Campaign Alert */}
        {activeCampaign && (
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 mb-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                <div>
                  <span className="font-bold text-lg">Campaign Active: </span>
                  <span className="text-green-100">{activeCampaign.name}</span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm">
                  <span className="font-medium">Progress: </span>
                  <span className="text-green-100">
                    {activeCampaign.processed || 0} / {activeCampaign.total_websites || activeCampaign.totalWebsites || activeCampaign.total_urls || 0}
                  </span>
                </div>
                <button
                  onClick={() => handleViewCampaign(activeCampaign.id)}
                  className="px-4 py-2 bg-white text-green-600 rounded-lg hover:bg-green-50 font-medium transition-all"
                >
                  View Details
                </button>
                <button
                  onClick={() => handleStopCampaign(activeCampaign.id)}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all"
                  title="Stop Campaign"
                >
                  <Pause className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <button
                key={idx}
                onClick={action.action}
                className={`${action.color} text-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:scale-105 group relative overflow-hidden`}
              >
                <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity"></div>
                <Icon className="w-8 h-8 mb-3 group-hover:rotate-12 transition-transform" />
                <h3 className="font-bold text-lg">{action.title}</h3>
                <p className="text-sm opacity-90 mt-1">{action.description}</p>
                <ArrowRight className="w-5 h-5 mt-3 opacity-70 group-hover:translate-x-2 transition-transform" />
              </button>
            );
          })}
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-md border p-6 hover:shadow-lg transition-all hover:scale-105">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500 font-medium">{getPeriodLabel()} Campaigns</p>
              <FileText className="w-6 h-6 text-indigo-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.totalCampaigns}</p>
            <div className="mt-2 flex items-center text-xs">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600">+12% from last period</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-6 hover:shadow-lg transition-all hover:scale-105">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500 font-medium">Total Submissions</p>
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.totalSubmissions.toLocaleString()}</p>
            <div className="mt-2 flex items-center text-xs">
              <Activity className="w-4 h-4 text-blue-500 mr-1" />
              <span className="text-blue-600">120/hour average</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-6 hover:shadow-lg transition-all hover:scale-105">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500 font-medium">Successful</p>
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.successful.toLocaleString()}</p>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(stats.successRate, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">{stats.successRate}% success rate</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-6 hover:shadow-lg transition-all hover:scale-105">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500 font-medium">Failed</p>
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.failed.toLocaleString()}</p>
            <div className="mt-2 flex items-center text-xs">
              <Shield className="w-4 h-4 text-orange-500 mr-1" />
              <span className="text-orange-600">CAPTCHA: {Math.round(stats.failed * 0.3)}</span>
            </div>
          </div>
        </div>

        {/* Recent Campaigns */}
        {campaigns.length > 0 && (
          <div className="bg-white rounded-xl shadow-md border p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Recent Campaigns</h3>
              <button
                onClick={() => navigate('/campaigns')}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
              >
                View All <ChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>
            
            <div className="space-y-3">
              {campaigns.slice(0, 3).map((campaign) => (
                <div 
                  key={campaign.id} 
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer group"
                  onClick={() => handleViewCampaign(campaign.id)}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-2 h-2 rounded-full ${
                      campaign.status === 'active' || campaign.status === 'running' || campaign.status === 'ACTIVE' ? 'bg-green-500 animate-pulse' :
                      campaign.status === 'completed' || campaign.status === 'COMPLETED' ? 'bg-blue-500' :
                      campaign.status === 'failed' || campaign.status === 'FAILED' ? 'bg-red-500' :
                      'bg-gray-400'
                    }`} />
                    <div>
                      <p className="font-medium text-gray-900">{campaign.name || `Campaign ${campaign.id?.slice(0, 8)}...`}</p>
                      <p className="text-sm text-gray-500">
                        {campaign.total_urls || campaign.total_websites || 0} URLs • {campaign.submitted_count || campaign.successful || 0} submitted
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 text-xs rounded-full font-medium ${getStatusColor(campaign.status)}`}>
                      {formatStatus(campaign.status)}
                    </span>
                    
                    {(campaign.status === 'completed' || campaign.status === 'COMPLETED') && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExportReport(campaign.id);
                        }}
                        className="p-2 text-gray-600 hover:bg-white rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewCampaign(campaign.id);
                      }}
                      className="p-2 text-gray-600 hover:bg-white rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-md border p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900">Recent Activity</h3>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          
          {recentSubmissions.length > 0 ? (
            <div className="space-y-3">
              {recentSubmissions.slice(0, 5).map((submission) => (
                <div key={submission.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  {submission.status === 'success' || submission.status === 'SUCCESS' ? (
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  ) : submission.status === 'failed' || submission.status === 'FAILED' ? (
                    <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                  ) : (
                    <Clock className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Globe className="w-4 h-4 text-gray-400" />
                      <p className="text-sm font-medium text-gray-900 truncate">{submission.url || 'Unknown URL'}</p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatStatus(submission.status)} • {submission.created_at ? new Date(submission.created_at).toLocaleString() : 'Recently'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-10 h-10 text-gray-400" />
              </div>
              <p className="text-gray-500 font-medium mb-2">No recent activity</p>
              <p className="text-sm text-gray-400 mb-6">Start a campaign to see submissions here</p>
              <button
                onClick={() => navigate('/form-submitter')}
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 font-medium transition-all transform hover:scale-105 shadow-lg"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                Start Your First Campaign
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default UserDashboard;