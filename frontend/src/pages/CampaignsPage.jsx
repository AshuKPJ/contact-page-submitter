// src/pages/CampaignsPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Search, Filter, MoreVertical, Play, Pause, CheckCircle, 
  XCircle, Clock, FileText, Calendar, TrendingUp, Eye, Trash2,
  AlertCircle, Download, RefreshCw
} from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const CampaignsPage = () => {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

  // Mock data - replace with API call
  const mockCampaigns = [
    {
      id: '1',
      name: 'Tech Companies Outreach',
      fileName: 'tech_companies_500.csv',
      status: 'completed',
      totalWebsites: 500,
      processed: 500,
      successful: 478,
      failed: 22,
      successRate: 95.6,
      startTime: '2024-01-15T09:00:00Z',
      endTime: '2024-01-15T15:30:00Z',
      duration: '6h 30m'
    },
    {
      id: '2', 
      name: 'SaaS Startups Campaign',
      fileName: 'saas_startups_1200.csv',
      status: 'running',
      totalWebsites: 1200,
      processed: 847,
      successful: 809,
      failed: 38,
      successRate: 95.5,
      startTime: '2024-01-16T08:15:00Z',
      endTime: null,
      estimatedEnd: '2024-01-16T18:45:00Z'
    },
    {
      id: '3',
      name: 'Healthcare Providers',
      fileName: 'healthcare_providers_300.csv', 
      status: 'failed',
      totalWebsites: 300,
      processed: 87,
      successful: 45,
      failed: 42,
      successRate: 51.7,
      startTime: '2024-01-14T10:00:00Z',
      endTime: '2024-01-14T11:30:00Z',
      errorMessage: 'CAPTCHA service unavailable'
    },
    {
      id: '4',
      name: 'E-commerce Sites',
      fileName: 'ecommerce_sites_800.csv',
      status: 'paused', 
      totalWebsites: 800,
      processed: 234,
      successful: 218,
      failed: 16,
      successRate: 93.2,
      startTime: '2024-01-13T14:20:00Z',
      pausedAt: '2024-01-13T16:45:00Z'
    }
  ];

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/campaigns');
      // setCampaigns(response.data);
      
      // Simulate API call
      setTimeout(() => {
        setCampaigns(mockCampaigns);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      toast.error('Failed to load campaigns');
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <Play className="w-4 h-4 text-green-600" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-blue-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'paused':
        return <Pause className="w-4 h-4 text-yellow-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleViewCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleNewCampaign = () => {
    navigate('/form-submitter');
  };

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         campaign.fileName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading campaigns...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
              <p className="text-gray-600">Manage your outreach campaigns</p>
            </div>
            <button
              onClick={handleNewCampaign}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>New Campaign</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">{campaigns.length}</p>
              </div>
              <FileText className="w-8 h-8 text-indigo-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Running Now</p>
                <p className="text-2xl font-bold text-green-600">
                  {campaigns.filter(c => c.status === 'running').length}
                </p>
              </div>
              <Play className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Success Rate</p>
                <p className="text-2xl font-bold text-blue-600">
                  {Math.round(campaigns.reduce((acc, c) => acc + c.successRate, 0) / campaigns.length)}%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Processed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {campaigns.reduce((acc, c) => acc + c.processed, 0).toLocaleString()}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-gray-600" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search campaigns..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="all">All Status</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="paused">Paused</option>
                <option value="failed">Failed</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="created_at">Newest First</option>
                <option value="name">Name</option>
                <option value="status">Status</option>
                <option value="success_rate">Success Rate</option>
              </select>
            </div>
          </div>
        </div>

        {/* Campaigns Table */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCampaigns.map((campaign) => (
                  <tr key={campaign.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {campaign.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {campaign.fileName} • {campaign.totalWebsites.toLocaleString()} websites
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                        {getStatusIcon(campaign.status)}
                        <span className="ml-1 capitalize">{campaign.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full">
                        <div className="text-xs text-gray-600 mb-1">
                          {campaign.processed} / {campaign.totalWebsites}
                        </div>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              campaign.status === 'running' ? 'bg-green-500' :
                              campaign.status === 'completed' ? 'bg-blue-500' :
                              campaign.status === 'failed' ? 'bg-red-500' :
                              'bg-yellow-500'
                            }`}
                            style={{ width: `${(campaign.processed / campaign.totalWebsites) * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{campaign.successRate}%</div>
                      <div className="text-xs text-gray-500">
                        {campaign.successful} success • {campaign.failed} failed
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(campaign.startTime)}
                      {campaign.duration && (
                        <div className="text-xs text-gray-400">{campaign.duration}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleViewCampaign(campaign.id)}
                          className="text-indigo-600 hover:text-indigo-700"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {campaign.status === 'completed' && (
                          <button
                            className="text-green-600 hover:text-green-700"
                            title="Download Report"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                        <button className="text-gray-400 hover:text-gray-600">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredCampaigns.length === 0 && (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">
              {campaigns.length === 0 ? 'No campaigns yet' : 'No campaigns match your filters'}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              {campaigns.length === 0 ? 'Create your first campaign to get started' : 'Try adjusting your search or filters'}
            </p>
            {campaigns.length === 0 && (
              <button
                onClick={handleNewCampaign}
                className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Create Campaign
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignsPage;