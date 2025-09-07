// UserDashboard.jsx - Complete Production Version
// This connects to your REAL PostgreSQL database via FastAPI

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, CheckCircle, Clock, Mail, Globe, AlertCircle, Upload, 
  FileText, TrendingUp, BarChart3, Activity, Target, RefreshCw, 
  Loader, X, Download, Settings, LogOut, User, Pause
} from 'lucide-react';

// ============================================================================
// API CONFIGURATION
// ============================================================================
const API_BASE_URL = 'http://localhost:8000'; // Change this for production

// ============================================================================
// API SERVICE LAYER
// ============================================================================
class APIService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers
        }
      });

      if (response.status === 401) {
        // Token expired - redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return null;
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Auth endpoints
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async logout() {
    return this.request('/api/auth/logout', { method: 'POST' });
  }

  // Campaign endpoints
  async getCampaigns(page = 1, perPage = 10) {
    return this.request(`/api/campaigns?page=${page}&per_page=${perPage}`);
  }

  async getCampaign(id) {
    return this.request(`/api/campaigns/${id}`);
  }

  async createCampaign(data) {
    return this.request('/api/campaigns', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async startCampaign(id) {
    return this.request(`/api/campaigns/${id}/start`, { method: 'POST' });
  }

  async stopCampaign(id) {
    return this.request(`/api/campaigns/${id}/stop`, { method: 'POST' });
  }

  async getCampaignStats(id) {
    return this.request(`/api/campaigns/${id}/stats`);
  }

  async uploadCSV(campaignId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('access_token');
    return fetch(`${this.baseURL}/api/campaigns/${campaignId}/upload-csv`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData
    }).then(res => res.json());
  }

  // Analytics endpoints
  async getUserAnalytics() {
    return this.request('/api/analytics/user');
  }

  async getDailyStats(days = 30) {
    return this.request(`/api/analytics/daily-stats?days=${days}`);
  }

  async getCampaignAnalytics(campaignId) {
    return this.request(`/api/analytics/campaign/${campaignId}`);
  }

  // Submission endpoints
  async getSubmissions(page = 1, perPage = 10, campaignId = null) {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    });
    
    if (campaignId) {
      params.append('campaign_id', campaignId);
    }
    
    return this.request(`/api/submissions?${params}`);
  }

  async retryFailedSubmissions(campaignId) {
    return this.request(`/api/submissions/${campaignId}/retry-failed`, {
      method: 'POST'
    });
  }

  // User endpoints
  async getUserProfile() {
    return this.request('/api/users/profile');
  }

  async updateProfile(data) {
    return this.request('/api/users/profile', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
}

// Create API instance
const api = new APIService();

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================
const UserDashboard = () => {
  const navigate = useNavigate();

  // State management
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  
  // Data from database
  const [campaigns, setCampaigns] = useState([]);
  const [currentCampaign, setCurrentCampaign] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  
  // UI state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);

  // ============================================================================
  // DATA FETCHING
  // ============================================================================
  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      
      // Fetch all data in parallel
      const [
        campaignsData,
        analyticsData,
        dailyStatsData,
        submissionsData,
        profileData
      ] = await Promise.all([
        api.getCampaigns(1, 10),
        api.getUserAnalytics(),
        api.getDailyStats(30),
        api.getSubmissions(1, 10),
        api.getUserProfile().catch(() => null)
      ]);

      // Process campaigns
      setCampaigns(campaignsData.campaigns || []);
      
      // Find running campaign and get detailed stats
      const runningCampaign = campaignsData.campaigns?.find(c => 
        c.status === 'running' || c.status === 'processing'
      );
      
      if (runningCampaign) {
        const stats = await api.getCampaignStats(runningCampaign.id);
        setCurrentCampaign({
          ...runningCampaign,
          ...stats
        });
      } else {
        setCurrentCampaign(null);
      }

      setUserAnalytics(analyticsData);
      setDailyStats(dailyStatsData || []);
      setRecentSubmissions(submissionsData.submissions || []);
      setUserProfile(profileData);

    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Initial load and auto-refresh
  useEffect(() => {
    fetchDashboardData();

    // Auto-refresh every 10 seconds if campaign is running
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        const hasRunningCampaign = campaigns.some(c => 
          c.status === 'running' || c.status === 'processing'
        );
        
        if (hasRunningCampaign) {
          fetchDashboardData();
        }
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [campaigns.length]);

  // ============================================================================
  // ACTION HANDLERS
  // ============================================================================
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
  };

  const handleStartCampaign = async (campaignId) => {
    try {
      await api.startCampaign(campaignId);
      await fetchDashboardData();
    } catch (err) {
      alert(`Failed to start campaign: ${err.message}`);
    }
  };

  const handleStopCampaign = async () => {
    if (!currentCampaign) return;
    
    if (window.confirm('Are you sure you want to stop this campaign?')) {
      try {
        await api.stopCampaign(currentCampaign.id);
        await fetchDashboardData();
      } catch (err) {
        alert(`Failed to stop campaign: ${err.message}`);
      }
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || !currentCampaign) return;
    
    setUploadProgress('Uploading...');
    
    try {
      const result = await api.uploadCSV(currentCampaign.id, selectedFile);
      setUploadProgress(`Success! Imported ${result.imported} websites.`);
      await fetchDashboardData();
      
      setTimeout(() => {
        setShowUploadModal(false);
        setSelectedFile(null);
        setUploadProgress(null);
      }, 2000);
    } catch (err) {
      setUploadProgress(`Error: ${err.message}`);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (err) {
      // Continue with logout even if API call fails
    }
    
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  // ============================================================================
  // DATA PROCESSING
  // ============================================================================
  const calculateStats = () => {
    const stats = userAnalytics?.stats || {};
    return {
      total: stats.total_submissions || 0,
      successful: stats.successful_submissions || 0,
      failed: stats.failed_submissions || 0,
      pending: stats.pending_submissions || 0,
      successRate: stats.success_rate || 0
    };
  };

  const processChartData = () => {
    if (!dailyStats || dailyStats.length === 0) {
      return { monthlyData: [], weeklyData: [] };
    }

    // Process monthly data
    const monthlyMap = new Map();
    dailyStats.forEach(stat => {
      const date = new Date(stat.date);
      const monthKey = date.toLocaleDateString('en-US', { month: 'short' });
      monthlyMap.set(monthKey, (monthlyMap.get(monthKey) || 0) + (stat.total || 0));
    });

    const monthlyData = Array.from(monthlyMap, ([month, count]) => ({ month, count }));

    // Process weekly data (last 7 days)
    const weeklyData = dailyStats.slice(-7).map(stat => ({
      day: new Date(stat.date).toLocaleDateString('en-US', { weekday: 'short' }),
      count: stat.total || 0
    }));

    return { monthlyData, weeklyData };
  };

  const stats = calculateStats();
  const { monthlyData, weeklyData } = processChartData();

  // ============================================================================
  // LOADING & ERROR STATES
  // ============================================================================
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !campaigns.length && !userAnalytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-sm border max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
            Connection Error
          </h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={fetchDashboardData}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Try Again
            </button>
            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // MAIN RENDER
  // ============================================================================
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              {userProfile && (
                <span className="text-sm text-gray-600">
                  Welcome, {userProfile.first_name || userProfile.email}
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
              
              <button
                onClick={() => navigate('/settings')}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Campaign Status Section */}
        {currentCampaign ? (
          <ActiveCampaignCard 
            campaign={currentCampaign}
            onStop={handleStopCampaign}
            onUpload={() => setShowUploadModal(true)}
          />
        ) : (
          <IdleCampaignCard 
            lastCampaign={campaigns[0]}
            onCreate={() => navigate('/campaigns/new')}
            onUpdateProfile={() => navigate('/profile')}
          />
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Submissions"
            value={stats.total}
            icon={<CheckCircle className="w-5 h-5 text-blue-600" />}
            color="blue"
          />
          <StatCard
            title="Successful"
            value={stats.successful}
            icon={<CheckCircle className="w-5 h-5 text-green-600" />}
            color="green"
            subtitle={`${stats.successRate}% success rate`}
          />
          <StatCard
            title="Failed"
            value={stats.failed}
            icon={<AlertCircle className="w-5 h-5 text-red-600" />}
            color="red"
          />
          <StatCard
            title="Pending"
            value={stats.pending}
            icon={<Clock className="w-5 h-5 text-yellow-600" />}
            color="yellow"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {monthlyData.length > 0 && (
            <ChartCard title="Monthly Submissions" data={monthlyData} type="bar" />
          )}
          {weeklyData.length > 0 && (
            <ChartCard title="Weekly Activity" data={weeklyData} type="line" />
          )}
        </div>

        {/* Recent Activity */}
        <RecentActivityCard submissions={recentSubmissions} />

        {/* Campaigns List */}
        {campaigns.length > 0 && (
          <CampaignsListCard 
            campaigns={campaigns}
            onStart={handleStartCampaign}
            onView={(id) => navigate(`/campaigns/${id}`)}
          />
        )}
      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onUpload={handleFileUpload}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          uploadProgress={uploadProgress}
        />
      )}
    </div>
  );
};

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const ActiveCampaignCard = ({ campaign, onStop, onUpload }) => {
  const progress = campaign.total > 0 
    ? ((campaign.successful + campaign.failed) / campaign.total) * 100 
    : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <Play className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">{campaign.name}</h2>
            <p className="text-sm text-gray-500">ID: {campaign.id?.substring(0, 8)}...</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={onUpload}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Upload className="w-4 h-4 inline mr-1" />
            Add URLs
          </button>
          <button
            onClick={onStop}
            className="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            <Pause className="w-4 h-4 inline mr-1" />
            Stop
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span>{campaign.successful + campaign.failed} of {campaign.total}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4 text-center">
        <div>
          <p className="text-2xl font-bold">{campaign.total}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-green-600">{campaign.successful}</p>
          <p className="text-xs text-gray-500">Success</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-red-600">{campaign.failed}</p>
          <p className="text-xs text-gray-500">Failed</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-yellow-600">{campaign.pending}</p>
          <p className="text-xs text-gray-500">Pending</p>
        </div>
      </div>
    </div>
  );
};

const IdleCampaignCard = ({ lastCampaign, onCreate, onUpdateProfile }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-semibold">Campaign Status</h2>
      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">Idle</span>
    </div>
    
    {lastCampaign && (
      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <p className="text-xs text-gray-500 mb-2">LAST CAMPAIGN</p>
        <p className="font-medium">{lastCampaign.name}</p>
        <div className="grid grid-cols-3 gap-4 mt-3">
          <div>
            <p className="text-xl font-bold">{lastCampaign.total_urls}</p>
            <p className="text-xs text-gray-500">URLs</p>
          </div>
          <div>
            <p className="text-xl font-bold text-green-600">
              {lastCampaign.submitted_count}
            </p>
            <p className="text-xs text-gray-500">Submitted</p>
          </div>
          <div>
            <p className="text-xl font-bold">
              {new Date(lastCampaign.created_at).toLocaleDateString()}
            </p>
            <p className="text-xs text-gray-500">Date</p>
          </div>
        </div>
      </div>
    )}
    
    <div className="flex space-x-3">
      <button
        onClick={onCreate}
        className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
      >
        Start New Campaign
      </button>
      <button
        onClick={onUpdateProfile}
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
      >
        Update Profile
      </button>
    </div>
  </div>
);

const StatCard = ({ title, value, icon, color, subtitle }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6">
    <div className="flex items-center justify-between mb-2">
      <p className="text-sm text-gray-500">{title}</p>
      {icon}
    </div>
    <p className={`text-3xl font-bold text-${color}-600`}>
      {value.toLocaleString()}
    </p>
    {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
  </div>
);

const ChartCard = ({ title, data, type }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6">
    <h3 className="text-lg font-semibold mb-4">{title}</h3>
    <div className="h-64 flex items-end justify-around">
      {type === 'bar' && data.map((item, idx) => (
        <div key={idx} className="flex-1 mx-1 flex flex-col items-center">
          <div 
            className="w-full bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t hover:from-indigo-700"
            style={{ height: `${(item.count / Math.max(...data.map(d => d.count))) * 200}px` }}
          />
          <span className="text-xs mt-2">{item.month || item.day}</span>
        </div>
      ))}
    </div>
  </div>
);

const RecentActivityCard = ({ submissions }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
    <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
    {submissions.length > 0 ? (
      <div className="space-y-3">
        {submissions.map((sub) => (
          <div key={sub.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
            {sub.status === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
            ) : sub.status === 'failed' ? (
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            ) : (
              <Clock className="w-5 h-5 text-yellow-600 mt-0.5" />
            )}
            <div className="flex-1">
              <p className="text-sm font-medium">{sub.url || 'Unknown URL'}</p>
              <p className="text-xs text-gray-500">
                {sub.status} • {new Date(sub.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-center text-gray-500 py-8">No recent activity</p>
    )}
  </div>
);

const CampaignsListCard = ({ campaigns, onStart, onView }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6">
    <h3 className="text-lg font-semibold mb-4">All Campaigns</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="text-left text-sm text-gray-500 border-b">
          <tr>
            <th className="pb-2">Name</th>
            <th className="pb-2">Status</th>
            <th className="pb-2">URLs</th>
            <th className="pb-2">Success</th>
            <th className="pb-2">Created</th>
            <th className="pb-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.map((campaign) => (
            <tr key={campaign.id} className="border-b hover:bg-gray-50">
              <td className="py-3 font-medium">{campaign.name}</td>
              <td className="py-3">
                <span className={`px-2 py-1 text-xs rounded ${
                  campaign.status === 'completed' ? 'bg-green-100 text-green-700' :
                  campaign.status === 'running' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {campaign.status}
                </span>
              </td>
              <td className="py-3">{campaign.total_urls}</td>
              <td className="py-3">{campaign.submitted_count}</td>
              <td className="py-3 text-sm text-gray-500">
                {new Date(campaign.created_at).toLocaleDateString()}
              </td>
              <td className="py-3">
                <button
                  onClick={() => onView(campaign.id)}
                  className="text-sm text-indigo-600 hover:text-indigo-800 mr-3"
                >
                  View
                </button>
                {campaign.status === 'draft' && (
                  <button
                    onClick={() => onStart(campaign.id)}
                    className="text-sm text-green-600 hover:text-green-800"
                  >
                    Start
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const UploadModal = ({ onClose, onUpload, selectedFile, setSelectedFile, uploadProgress }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-lg p-6 max-w-md w-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Upload CSV File</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="mb-4">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setSelectedFile(e.target.files[0])}
          className="w-full p-2 border rounded-lg"
        />
      </div>
      
      {uploadProgress && (
        <div className="mb-4 p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">
          {uploadProgress}
        </div>
      )}
      
      <div className="flex space-x-3">
        <button
          onClick={onUpload}
          disabled={!selectedFile || uploadProgress}
          className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300"
        >
          Upload
        </button>
        <button
          onClick={onClose}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
);

export default UserDashboard;