// Timeline Design - Activity Page
import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { trackEvent } from '../services/telemetry';
import { 
  RefreshCw, Download, Filter, Activity, AlertCircle, Calendar, Search, 
  Clock, X, Check, AlertTriangle, Info, Server, Smartphone, Upload, 
  FileText, ExternalLink, ChevronDown, ChevronRight, Bookmark, Star
} from 'lucide-react';

const defaultFilters = {
  me: true,
  source: '',
  level: '',
  action: '',
  status: '',
  q: '',
  date_from: '',
  date_to: '',
  page: 1,
  page_size: 25,
};

const ActivityPage = () => {
  const [filters, setFilters] = useState(defaultFilters);
  const [resp, setResp] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [stats, setStats] = useState(null);
  const [expandedGroups, setExpandedGroups] = useState(new Set());
  const [pinnedItems, setPinnedItems] = useState(new Set());

  // ... (keeping the same utility functions as before)
  const cleanParams = (obj) => {
    const p = { ...obj };
    Object.keys(p).forEach((k) => {
      if (p[k] === '' || p[k] === null) {
        delete p[k];
      }
    });
    return p;
  };

  const loadStats = async () => {
    try {
      const params = { me: filters.me, date_from: filters.date_from, date_to: filters.date_to };
      const response = await api.get('/activity/stats', { params: cleanParams(params) });
      setStats(response.data);
    } catch (e) {
      console.error('Failed to load activity stats:', e);
    }
  };

  const load = async () => {
    setLoading(true);
    try {
      const params = cleanParams(filters);
      const r = await api.get('/activity/stream', { params });
      setResp(r.data);
    } catch (e) {
      console.error('Activity load failed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    loadStats();
  }, [filters.page, filters.page_size]);

  const setField = (k, v) => setFilters((f) => ({ ...f, [k]: v }));

  const getSourceIcon = (source) => {
    switch(source) {
      case 'system': return <Server className="w-5 h-5 text-slate-600" />;
      case 'app': return <Smartphone className="w-5 h-5 text-blue-600" />;
      case 'submission': return <Upload className="w-5 h-5 text-emerald-600" />;
      default: return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const getLevelColor = (level) => {
    switch(level) {
      case 'ERROR': return 'bg-red-500';
      case 'WARN': return 'bg-amber-500';
      case 'INFO': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  // Group activities by date
  const groupActivitiesByDate = (activities) => {
    const groups = {};
    activities.forEach(activity => {
      const date = new Date(activity.timestamp).toDateString();
      if (!groups[date]) groups[date] = [];
      groups[date].push(activity);
    });
    return groups;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();
    
    if (date.toDateString() === today) return 'Today';
    if (date.toDateString() === yesterday) return 'Yesterday';
    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  };

  const groupedActivities = groupActivitiesByDate(resp.items);

  const TimelineItem = ({ activity, isLast }) => (
    <div className="flex group">
      {/* Timeline Line */}
      <div className="flex flex-col items-center mr-4">
        <div className={`w-3 h-3 rounded-full ${getLevelColor(activity.title || 'INFO')} ring-4 ring-white shadow-sm`} />
        {!isLast && <div className="w-px h-full bg-gray-200 mt-2" />}
      </div>
      
      {/* Content */}
      <div className="flex-1 pb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition-all duration-200 group-hover:border-gray-300">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-50">
                {getSourceIcon(activity.source)}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900">
                    {activity.action || activity.source.charAt(0).toUpperCase() + activity.source.slice(1)}
                  </span>
                  {activity.status && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      activity.status.toLowerCase().includes('success') ? 'bg-emerald-100 text-emerald-700' :
                      activity.status.toLowerCase().includes('fail') ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {activity.status}
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setPinnedItems(prev => 
                prev.has(activity.id) 
                  ? new Set([...prev].filter(id => id !== activity.id))
                  : new Set([...prev, activity.id])
              )}
              className="text-gray-400 hover:text-amber-500 transition-colors"
            >
              <Star className={`w-4 h-4 ${pinnedItems.has(activity.id) ? 'fill-current text-amber-500' : ''}`} />
            </button>
          </div>
          
          {activity.message && (
            <p className="text-gray-700 mb-3 leading-relaxed">{activity.message}</p>
          )}
          
          {activity.details && (
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600 mb-3">
              {activity.details}
            </div>
          )}
          
          {activity.target_url && (
            <a
              href={activity.target_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              View Resource
            </a>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Activity Timeline</h1>
              <p className="text-gray-600 mt-1">Track and monitor all system activities</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={load}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={() => {}}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Filters & Stats */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Activity Summary</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500" />
                    <span className="text-sm text-gray-600">Info</span>
                  </div>
                  <span className="font-semibold">{stats?.by_level?.INFO || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-amber-500" />
                    <span className="text-sm text-gray-600">Warnings</span>
                  </div>
                  <span className="font-semibold">{stats?.by_level?.WARN || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-sm text-gray-600">Errors</span>
                  </div>
                  <span className="font-semibold">{stats?.by_level?.ERROR || 0}</span>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
                  <select
                    value={filters.source}
                    onChange={(e) => setField('source', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="">All Sources</option>
                    <option value="system">System</option>
                    <option value="app">Application</option>
                    <option value="submission">Submission</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Level</label>
                  <select
                    value={filters.level}
                    onChange={(e) => setField('level', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="">All Levels</option>
                    <option value="INFO">Info</option>
                    <option value="WARN">Warning</option>
                    <option value="ERROR">Error</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                  <input
                    value={filters.q}
                    onChange={(e) => setField('q', e.target.value)}
                    placeholder="Search activities..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>

                <button
                  onClick={() => { load(); loadStats(); }}
                  className="w-full bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>

          {/* Main Timeline */}
          <div className="lg:col-span-3">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            )}
            
            {!loading && resp.items.length === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Activities Found</h3>
                <p className="text-gray-600">Try adjusting your filters or check back later.</p>
              </div>
            )}

            {!loading && Object.keys(groupedActivities).length > 0 && (
              <div className="space-y-8">
                {Object.entries(groupedActivities).map(([date, activities]) => (
                  <div key={date}>
                    <div className="sticky top-4 z-10 mb-6">
                      <div className="bg-white rounded-lg border border-gray-200 px-4 py-2 shadow-sm">
                        <button
                          onClick={() => setExpandedGroups(prev => 
                            prev.has(date) 
                              ? new Set([...prev].filter(d => d !== date))
                              : new Set([...prev, date])
                          )}
                          className="flex items-center gap-2 w-full text-left"
                        >
                          {expandedGroups.has(date) ? 
                            <ChevronDown className="w-4 h-4" /> : 
                            <ChevronRight className="w-4 h-4" />
                          }
                          <h2 className="font-semibold text-gray-900">{formatDate(date)}</h2>
                          <span className="text-sm text-gray-500">({activities.length} activities)</span>
                        </button>
                      </div>
                    </div>

                    {(!expandedGroups.size || expandedGroups.has(date)) && (
                      <div className="pl-4">
                        {activities.map((activity, index) => (
                          <TimelineItem 
                            key={activity.id || index}
                            activity={activity}
                            isLast={index === activities.length - 1}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityPage;