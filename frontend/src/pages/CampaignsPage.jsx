// src/pages/CampaignsPage.jsx - Enhanced Complete Version
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Plus, Play, Pause, Trash2, Edit, BarChart, Clock, CheckCircle,
  XCircle, RefreshCw, Activity, Target, FileText, TrendingUp,
  AlertCircle, Eye, Download, Upload, Search, Filter, Zap,
  Calendar, MoreVertical, ArrowUp, ArrowDown, ChevronLeft,
  ChevronRight, Mail, Globe, Shield
} from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";
import AlertMessage from "../components/AlertMessage";

const CampaignsPage = () => {
  const navigate = useNavigate();
  
  // State Management
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("created_desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [campaignToDelete, setCampaignToDelete] = useState(null);
  
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    completed: 0,
    failed: 0,
    draft: 0,
    totalProcessed: 0,
    avgSuccessRate: 0,
  });

  // Fetch campaigns from backend
  const fetchCampaigns = async (silent = false) => {
    try {
      setError(null);
      if (!loading && !silent) setRefreshing(true);

      console.log("[CAMPAIGNS] Fetching campaigns...");

      const response = await api.get("/campaigns");
      const data = response.data;

      // Handle different response formats
      let campaignsData = [];
      if (Array.isArray(data)) {
        campaignsData = data;
      } else if (data?.campaigns) {
        campaignsData = data.campaigns;
      } else if (data?.items) {
        campaignsData = data.items;
      }

      // Normalize campaign data
      const normalizedCampaigns = campaignsData.map((campaign) => ({
        id: campaign.id || campaign._id,
        name: campaign.name || `Campaign #${campaign.id}`,
        fileName: campaign.file_name || campaign.fileName || "unknown.csv",
        status: campaign.status?.toLowerCase() || "draft",
        totalWebsites: campaign.total_websites || campaign.totalWebsites || campaign.total_urls || 0,
        processed: campaign.processed || 0,
        successful: campaign.successful || campaign.submitted_count || 0,
        failed: campaign.failed || campaign.failed_count || 0,
        emailFallback: campaign.email_fallback || campaign.emailFallback || 0,
        noForm: campaign.no_form || campaign.noForm || 0,
        startTime: campaign.start_time || campaign.startTime || campaign.created_at,
        endTime: campaign.end_time || campaign.endTime,
        successRate: campaign.success_rate || calculateSuccessRate(campaign),
        createdAt: campaign.created_at || campaign.createdAt,
        updatedAt: campaign.updated_at || campaign.updatedAt,
      }));

      setCampaigns(normalizedCampaigns);

      // Calculate statistics
      const stats = calculateStats(normalizedCampaigns);
      setStats(stats);

      console.log("[CAMPAIGNS] Loaded", normalizedCampaigns.length, "campaigns");
      
    } catch (err) {
      console.error("[CAMPAIGNS] Error:", err);

      let errorMessage = "Failed to load campaigns";
      if (!navigator.onLine) {
        errorMessage = "No internet connection";
      } else if (err.response?.status === 401) {
        errorMessage = "Session expired. Please login again.";
        navigate('/');
      }

      setError(errorMessage);
      if (!silent) toast.error(errorMessage);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Calculate success rate
  const calculateSuccessRate = (campaign) => {
    const total = campaign.processed || 0;
    const successful = campaign.successful || campaign.submitted_count || 0;
    return total > 0 ? Math.round((successful / total) * 100) : 0;
  };

  // Calculate statistics
  const calculateStats = (campaignsList) => {
    const activeCount = campaignsList.filter(c => 
      c.status === "running" || c.status === "active"
    ).length;

    const completedCount = campaignsList.filter(c => 
      c.status === "completed"
    ).length;

    const failedCount = campaignsList.filter(c => 
      c.status === "failed"
    ).length;

    const draftCount = campaignsList.filter(c => 
      c.status === "draft" || c.status === "ready"
    ).length;

    const totalProcessed = campaignsList.reduce(
      (sum, c) => sum + (c.processed || 0), 0
    );

    const avgSuccessRate = campaignsList.length > 0
      ? campaignsList.reduce((sum, c) => sum + (c.successRate || 0), 0) / campaignsList.length
      : 0;

    return {
      total: campaignsList.length,
      active: activeCount,
      completed: completedCount,
      failed: failedCount,
      draft: draftCount,
      totalProcessed,
      avgSuccessRate
    };
  };

  // Initial load
  useEffect(() => {
    fetchCampaigns();
  }, []);

  // Auto-refresh for active campaigns
  useEffect(() => {
    if (stats.active > 0) {
      const interval = setInterval(() => {
        if (document.visibilityState === "visible") {
          fetchCampaigns(true); // Silent refresh
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [stats.active]);

  // Campaign actions
  const handleStartCampaign = async (campaignId, e) => {
    e.stopPropagation();
    
    const toastId = toast.loading('Starting campaign...');
    try {
      await api.post(`/campaigns/${campaignId}/start`);
      toast.success("Campaign started successfully", { id: toastId });
      fetchCampaigns();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to start campaign", { id: toastId });
    }
  };

  const handleStopCampaign = async (campaignId, e) => {
    e.stopPropagation();
    
    if (!window.confirm("Are you sure you want to stop this campaign?")) return;
    
    const toastId = toast.loading('Stopping campaign...');
    try {
      await api.post(`/campaigns/${campaignId}/stop`);
      toast.success("Campaign stopped successfully", { id: toastId });
      fetchCampaigns();
    } catch (err) {
      toast.error("Failed to stop campaign", { id: toastId });
    }
  };

  const handleDeleteCampaign = async () => {
    if (!campaignToDelete) return;
    
    const toastId = toast.loading('Deleting campaign...');
    try {
      await api.delete(`/campaigns/${campaignToDelete.id}`);
      toast.success("Campaign deleted successfully", { id: toastId });
      setShowDeleteModal(false);
      setCampaignToDelete(null);
      fetchCampaigns();
    } catch (err) {
      toast.error("Failed to delete campaign", { id: toastId });
    }
  };

  const handleCreateCampaign = () => {
    navigate('/campaigns/new');
  };

  const handleViewCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleExportCampaign = async (campaignId, e) => {
    e.stopPropagation();
    
    const toastId = toast.loading('Preparing download...');
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
      toast.success('Report downloaded successfully', { id: toastId });
    } catch (err) {
      toast.error('Failed to download report', { id: toastId });
    }
  };

  // Sorting function
  const sortCampaigns = (campaignsList) => {
    const sorted = [...campaignsList];
    
    switch (sortBy) {
      case 'created_desc':
        return sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      case 'created_asc':
        return sorted.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      case 'name_asc':
        return sorted.sort((a, b) => a.name.localeCompare(b.name));
      case 'name_desc':
        return sorted.sort((a, b) => b.name.localeCompare(a.name));
      case 'success_desc':
        return sorted.sort((a, b) => b.successRate - a.successRate);
      case 'success_asc':
        return sorted.sort((a, b) => a.successRate - b.successRate);
      default:
        return sorted;
    }
  };

  // Filter and sort campaigns
  const getFilteredCampaigns = () => {
    let filtered = campaigns.filter(campaign => {
      const matchesSearch = campaign.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           campaign.fileName.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
    
    return sortCampaigns(filtered);
  };

  // Pagination
  const filteredCampaigns = getFilteredCampaigns();
  const totalPages = Math.ceil(filteredCampaigns.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedCampaigns = filteredCampaigns.slice(startIndex, startIndex + itemsPerPage);

  // Get status display
  const getStatusDisplay = (status) => {
    const statusMap = {
      draft: { 
        color: "bg-gray-100 text-gray-700", 
        label: "Draft",
        icon: Edit
      },
      ready: { 
        color: "bg-blue-100 text-blue-700", 
        label: "Ready",
        icon: Clock
      },
      running: { 
        color: "bg-green-100 text-green-700", 
        label: "Running",
        icon: Play,
        animated: true
      },
      active: { 
        color: "bg-green-100 text-green-700", 
        label: "Active",
        icon: Activity,
        animated: true
      },
      paused: { 
        color: "bg-yellow-100 text-yellow-700", 
        label: "Paused",
        icon: Pause
      },
      completed: { 
        color: "bg-blue-100 text-blue-700", 
        label: "Completed",
        icon: CheckCircle
      },
      failed: { 
        color: "bg-red-100 text-red-700", 
        label: "Failed",
        icon: XCircle
      },
      stopped: { 
        color: "bg-gray-100 text-gray-700", 
        label: "Stopped",
        icon: XCircle
      },
    };

    return statusMap[status?.toLowerCase()] || statusMap["draft"];
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Format duration
  const formatDuration = (startTime, endTime) => {
    if (!startTime) return "N/A";
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

  // Loading state
  if (loading && campaigns.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
            <div className="absolute inset-0 animate-pulse rounded-full h-16 w-16 border-t-2 border-purple-600 mx-auto"></div>
          </div>
          <p className="mt-4 text-gray-600 font-medium">Loading campaigns...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Campaigns
              </h1>
              <p className="text-gray-600 mt-1">Manage your automated outreach campaigns</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => fetchCampaigns()}
                disabled={refreshing}
                className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
                Refresh
              </button>
              <button
                onClick={handleCreateCampaign}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all transform hover:scale-105"
              >
                <Plus className="w-5 h-5" />
                New Campaign
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <BarChart className="w-8 h-8 text-indigo-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <Activity className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Draft</p>
                <p className="text-2xl font-bold text-gray-600">{stats.draft}</p>
              </div>
              <Edit className="w-8 h-8 text-gray-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-blue-600">{stats.completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Processed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.totalProcessed > 999 
                    ? `${(stats.totalProcessed / 1000).toFixed(1)}K`
                    : stats.totalProcessed}
                </p>
              </div>
              <FileText className="w-8 h-8 text-gray-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border p-4 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {stats.avgSuccessRate.toFixed(0)}%
                </p>
              </div>
              <Target className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-md border p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search campaigns..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="stopped">Stopped</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="created_desc">Newest First</option>
                <option value="created_asc">Oldest First</option>
                <option value="name_asc">Name A-Z</option>
                <option value="name_desc">Name Z-A</option>
                <option value="success_desc">Highest Success</option>
                <option value="success_asc">Lowest Success</option>
              </select>
              
              <select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="5">5 per page</option>
                <option value="10">10 per page</option>
                <option value="25">25 per page</option>
                <option value="50">50 per page</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <AlertMessage
            type="error"
            title="Error Loading Campaigns"
            message={error}
            onClose={() => setError(null)}
          />
        )}

        {/* Campaigns Table */}
        {paginatedCampaigns.length > 0 ? (
          <div className="bg-white rounded-xl shadow-md border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Campaign
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Success Rate
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedCampaigns.map((campaign) => {
                    const statusDisplay = getStatusDisplay(campaign.status);
                    const StatusIcon = statusDisplay.icon;
                    const progress = campaign.totalWebsites > 0
                      ? Math.round((campaign.processed / campaign.totalWebsites) * 100)
                      : 0;

                    return (
                      <tr
                        key={campaign.id}
                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => handleViewCampaign(campaign.id)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {campaign.name}
                            </div>
                            <div className="text-xs text-gray-500 flex items-center mt-1">
                              <FileText className="w-3 h-3 mr-1" />
                              {campaign.fileName} • {campaign.totalWebsites} URLs
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${statusDisplay.color}`}>
                            <StatusIcon className={`w-3 h-3 mr-1 ${statusDisplay.animated ? 'animate-pulse' : ''}`} />
                            {statusDisplay.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-1">
                              <div className="text-sm text-gray-900 font-medium">
                                {campaign.processed} / {campaign.totalWebsites}
                              </div>
                              <div className="mt-1 w-full bg-gray-200 rounded-full h-2.5">
                                <div
                                  className={`h-2.5 rounded-full transition-all ${
                                    progress < 50 ? 'bg-red-500' :
                                    progress < 80 ? 'bg-yellow-500' :
                                    'bg-green-500'
                                  }`}
                                  style={{ width: `${progress}%` }}
                                />
                              </div>
                            </div>
                            <span className="ml-3 text-sm font-medium text-gray-900">
                              {progress}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className={`text-sm font-medium ${
                              campaign.successRate >= 90 ? 'text-green-600' :
                              campaign.successRate >= 70 ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {campaign.successRate}%
                            </span>
                            {campaign.successRate >= 90 && (
                              <TrendingUp className="w-4 h-4 text-green-500 ml-1" />
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1 text-gray-400" />
                            {formatDuration(campaign.startTime, campaign.endTime)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1 text-gray-400" />
                            {formatDate(campaign.createdAt)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewCampaign(campaign.id);
                              }}
                              className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            
                            {(campaign.status === "draft" || campaign.status === "ready" || campaign.status === "stopped") && (
                              <button
                                onClick={(e) => handleStartCampaign(campaign.id, e)}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Start Campaign"
                              >
                                <Play className="w-4 h-4" />
                              </button>
                            )}
                            
                            {(campaign.status === "running" || campaign.status === "active") && (
                              <button
                                onClick={(e) => handleStopCampaign(campaign.id, e)}
                                className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                                title="Stop Campaign"
                              >
                                <Pause className="w-4 h-4" />
                              </button>
                            )}
                            
                            {campaign.status === "completed" && (
                              <button
                                onClick={(e) => handleExportCampaign(campaign.id, e)}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Download Report"
                              >
                                <Download className="w-4 h-4" />
                              </button>
                            )}
                            
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setCampaignToDelete(campaign);
                                setShowDeleteModal(true);
                              }}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Delete Campaign"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, filteredCampaigns.length)} of {filteredCampaigns.length} campaigns
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  
                  {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = idx + 1;
                    } else if (currentPage <= 3) {
                      pageNum = idx + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + idx;
                    } else {
                      pageNum = currentPage - 2 + idx;
                    }
                    
                    return (
                      <button
                        key={idx}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-3 py-1 rounded-lg border ${
                          currentPage === pageNum
                            ? 'bg-indigo-600 text-white border-indigo-600'
                            : 'border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          !loading && !error && (
            <div className="bg-white rounded-xl shadow-md border p-12">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart className="w-10 h-10 text-indigo-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {searchQuery || statusFilter !== 'all' 
                    ? 'No campaigns found' 
                    : 'No campaigns yet'}
                </h3>
                <p className="text-gray-500 mb-6">
                  {searchQuery || statusFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Start your first automated outreach campaign'}
                </p>
                {!searchQuery && statusFilter === 'all' && (
                  <button
                    onClick={handleCreateCampaign}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all transform hover:scale-105"
                  >
                    <Plus className="w-5 h-5" />
                    Create First Campaign
                  </button>
                )}
              </div>
            </div>
          )
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && campaignToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Delete Campaign</h3>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <span className="font-semibold">{campaignToDelete.name}</span>? 
              This action cannot be undone and all campaign data will be permanently removed.
            </p>
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setCampaignToDelete(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteCampaign}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
              >
                Delete Campaign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignsPage;