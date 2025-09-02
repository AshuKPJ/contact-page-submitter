import React, { useState } from "react";
import { 
  TrendingUp, Users, FileText, Shield, Activity, DollarSign, Clock, Mail, 
  Database, Server, HardDrive, Cpu, CheckCircle, AlertCircle, Settings, 
  RefreshCw, Download, Filter, Search, Calendar, MoreVertical, BarChart3,
  Target, Zap, Globe, UserCheck, AlertTriangle
} from "lucide-react";

const AdminDashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("month");
  const [activeTab, setActiveTab] = useState("overview");
  const [searchQuery, setSearchQuery] = useState("");

  // Enhanced stats with gradient colors
  const stats = [
    { 
      label: "Total Users", 
      value: "412", 
      icon: Users, 
      trend: "+12.5%", 
      trendUp: true,
      color: "from-blue-500 to-blue-600",
      lightColor: "bg-blue-100",
      iconColor: "text-blue-600",
      description: "Active accounts"
    },
    { 
      label: "Active Campaigns", 
      value: "8,243", 
      icon: Activity, 
      trend: "+8.2%", 
      trendUp: true,
      color: "from-purple-500 to-purple-600",
      lightColor: "bg-purple-100",
      iconColor: "text-purple-600",
      description: "Running now"
    },
    { 
      label: "Form Submissions", 
      value: "211K", 
      icon: FileText, 
      trend: "+23.1%", 
      trendUp: true,
      color: "from-green-500 to-green-600",
      lightColor: "bg-green-100",
      iconColor: "text-green-600",
      description: "This month"
    },
    { 
      label: "Success Rate", 
      value: "96.8%", 
      icon: Target, 
      trend: "+2.4%", 
      trendUp: true,
      color: "from-orange-500 to-orange-600",
      lightColor: "bg-orange-100",
      iconColor: "text-orange-600",
      description: "Average rate"
    },
  ];

  // Database health metrics
  const dbMetrics = {
    status: "healthy",
    tables: 24,
    totalRecords: "394.5K",
    dbSize: "1.2 GB",
    avgQueryTime: "23ms",
    activeConnections: 18,
    maxConnections: 100,
    cacheHitRate: 94.7,
    uptime: "99.99%"
  };

  // Monthly data for charts
  const monthlyData = [
    { month: 'Jan', users: 280, campaigns: 1200, submissions: 18500 },
    { month: 'Feb', users: 320, campaigns: 1900, submissions: 24300 },
    { month: 'Mar', users: 340, campaigns: 2400, submissions: 31200 },
    { month: 'Apr', users: 360, campaigns: 2100, submissions: 28900 },
    { month: 'May', users: 380, campaigns: 2800, submissions: 38400 },
  ];

  // Weekly activity data
  const weeklyActivity = [
    { day: 'Mon', submissions: 4200 },
    { day: 'Tue', submissions: 5800 },
    { day: 'Wed', submissions: 4900 },
    { day: 'Thu', submissions: 6200 },
    { day: 'Fri', submissions: 7100 },
    { day: 'Sat', submissions: 5500 },
    { day: 'Sun', submissions: 3800 },
  ];

  // Form types distribution
  const formTypes = [
    { label: 'Contact Forms', value: 45230, color: '#10B981', percentage: 42 },
    { label: 'Registration', value: 38940, color: '#F59E0B', percentage: 36 },
    { label: 'Surveys', value: 24100, color: '#EF4444', percentage: 22 },
  ];

  // Database tables
  const tableInfo = [
    { name: "users", records: 412, size: "8.4 MB", lastModified: "2 min ago", status: "optimal" },
    { name: "campaigns", records: 8243, size: "124.6 MB", lastModified: "5 min ago", status: "optimal" },
    { name: "submissions", records: 211875, size: "856.2 MB", lastModified: "Just now", status: "indexing" },
    { name: "captcha_logs", records: 173093, size: "234.5 MB", lastModified: "30 sec ago", status: "optimal" },
  ];

  // Recent activity
  const recentActivity = [
    { type: 'user', message: 'New user registered: john.doe@example.com', time: '2 minutes ago', icon: UserCheck, color: 'text-green-600' },
    { type: 'campaign', message: 'Campaign #8243 started processing', time: '5 minutes ago', icon: Activity, color: 'text-blue-600' },
    { type: 'error', message: 'Failed CAPTCHA validation for 3 submissions', time: '12 minutes ago', icon: AlertTriangle, color: 'text-red-600' },
    { type: 'system', message: 'Database backup completed successfully', time: '1 hour ago', icon: Database, color: 'text-purple-600' },
  ];

  const maxMonthlySubmissions = Math.max(...monthlyData.map(d => d.submissions));
  const maxWeeklyActivity = Math.max(...weeklyActivity.map(d => d.submissions));

  // Donut chart path calculation
  const createDonutPath = (value, total, startAngle) => {
    const percentage = value / total;
    const angle = percentage * 360;
    const endAngle = startAngle + angle;
    
    const outerRadius = 70;
    const innerRadius = 45;
    const cx = 85;
    const cy = 85;
    
    const x1 = cx + outerRadius * Math.cos((startAngle * Math.PI) / 180);
    const y1 = cy + outerRadius * Math.sin((startAngle * Math.PI) / 180);
    const x2 = cx + outerRadius * Math.cos((endAngle * Math.PI) / 180);
    const y2 = cy + outerRadius * Math.sin((endAngle * Math.PI) / 180);
    const x3 = cx + innerRadius * Math.cos((endAngle * Math.PI) / 180);
    const y3 = cy + innerRadius * Math.sin((endAngle * Math.PI) / 180);
    const x4 = cx + innerRadius * Math.cos((startAngle * Math.PI) / 180);
    const y4 = cy + innerRadius * Math.sin((startAngle * Math.PI) / 180);
    
    const largeArcFlag = angle > 180 ? 1 : 0;
    
    return `M ${x1} ${y1} A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
  };

  const donutTotal = formTypes.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -90;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">System overview and database management</p>
            </div>
            <div className="flex items-center space-x-3">
              <select 
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export Data</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* System Status Bar */}
        <div className={`rounded-lg p-4 mb-6 ${
          dbMetrics.status === 'healthy' 
            ? 'bg-green-500 text-white' 
            : 'bg-yellow-500 text-white'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
              <span className="font-semibold">System Status: All Services Operational</span>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Server className="w-4 h-4" />
                <span>{dbMetrics.activeConnections}/{dbMetrics.maxConnections} connections</span>
              </div>
              <div className="flex items-center space-x-2">
                <HardDrive className="w-4 h-4" />
                <span>{dbMetrics.dbSize} used</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>{dbMetrics.uptime} uptime</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div key={idx} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className={`${stat.lightColor} p-3 rounded-lg`}>
                    <Icon className={`w-5 h-5 ${stat.iconColor}`} />
                  </div>
                  <span className={`text-xs font-bold flex items-center ${
                    stat.trendUp ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <TrendingUp className={`w-3 h-3 mr-1 ${!stat.trendUp && 'rotate-180'}`} />
                    {stat.trend}
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-xs text-gray-400 mt-1">{stat.description}</p>
              </div>
            );
          })}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Monthly Submissions Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
              Monthly Submissions
            </h3>
            <div className="relative h-64">
              <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
                <span>40K</span>
                <span>30K</span>
                <span>20K</span>
                <span>10K</span>
                <span>0</span>
              </div>
              
              <div className="ml-10 h-full pb-8 relative">
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-gray-200"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-200"></div>
                </div>
                
                <div className="relative h-full flex items-end justify-around">
                  {monthlyData.map((item, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center mx-2 group">
                      <div className="relative w-full flex justify-center">
                        <div 
                          className="w-12 bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t hover:from-indigo-700 hover:to-indigo-500 transition-all cursor-pointer shadow-sm"
                          style={{ 
                            height: `${(item.submissions / 40000) * 192}px`
                          }}
                        >
                          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                            {item.submissions.toLocaleString()} submissions
                          </div>
                        </div>
                      </div>
                      <span className="text-sm text-gray-600 mt-2 font-medium">{item.month}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Form Types Distribution */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-indigo-600" />
              Form Types Distribution
            </h3>
            <div className="flex items-center justify-around">
              <div className="relative">
                <svg width="170" height="170" className="transform -rotate-90">
                  {formTypes.map((item, idx) => {
                    const path = createDonutPath(item.value, donutTotal, currentAngle);
                    const pathElement = (
                      <path
                        key={idx}
                        d={path}
                        fill={item.color}
                        className="hover:opacity-80 transition-opacity cursor-pointer"
                        stroke="white"
                        strokeWidth="2"
                      />
                    );
                    currentAngle += (item.value / donutTotal) * 360;
                    return pathElement;
                  })}
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-gray-900">{(donutTotal / 1000).toFixed(0)}K</p>
                    <p className="text-sm text-gray-500">Total</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                {formTypes.map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-3">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{item.label}</p>
                      <p className="text-xs text-gray-500">{item.percentage}% • {(item.value / 1000).toFixed(1)}K</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Activity Chart */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-indigo-600" />
            Weekly Activity
          </h3>
          <div className="relative h-64">
            <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
              <span>8K</span>
              <span>6K</span>
              <span>4K</span>
              <span>2K</span>
              <span>0</span>
            </div>
            
            <div className="ml-10 h-full pb-8 relative">
              <div className="absolute inset-0">
                <div className="h-full flex flex-col justify-between">
                  <div className="border-t border-gray-200"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-200"></div>
                </div>
              </div>
              
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 420 200">
                <defs>
                  <linearGradient id="adminLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#818CF8" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="#818CF8" stopOpacity="0" />
                  </linearGradient>
                </defs>
                
                {(() => {
                  const chartWidth = 420;
                  const chartHeight = 200;
                  const points = weeklyActivity.map((item, idx) => {
                    const x = (idx / (weeklyActivity.length - 1)) * chartWidth;
                    const y = chartHeight - (item.submissions / 8000) * chartHeight;
                    return `${x},${y}`;
                  });
                  
                  const areaPath = `M ${points[0]} L ${points.join(' L ')} L ${chartWidth},${chartHeight} L 0,${chartHeight} Z`;
                  
                  return (
                    <>
                      <path d={areaPath} fill="url(#adminLineGradient)" />
                      <polyline
                        points={points.join(' ')}
                        fill="none"
                        stroke="#818CF8"
                        strokeWidth="3"
                        strokeLinejoin="round"
                        strokeLinecap="round"
                      />
                      {weeklyActivity.map((item, idx) => {
                        const x = (idx / (weeklyActivity.length - 1)) * chartWidth;
                        const y = chartHeight - (item.submissions / 8000) * chartHeight;
                        return (
                          <g key={idx}>
                            <circle cx={x} cy={y} r="5" fill="white" stroke="#818CF8" strokeWidth="3" />
                            <circle cx={x} cy={y} r="12" fill="transparent" className="hover:fill-indigo-100 hover:fill-opacity-50 cursor-pointer" />
                          </g>
                        );
                      })}
                    </>
                  );
                })()}
              </svg>
              
              <div className="absolute inset-0">
                {weeklyActivity.map((item, idx) => {
                  const x = (idx / (weeklyActivity.length - 1)) * 100;
                  const y = 100 - (item.submissions / 8000) * 100;
                  return (
                    <div
                      key={idx}
                      className="absolute group"
                      style={{ 
                        left: `${x}%`, 
                        top: `${y}%`,
                        width: '20px',
                        height: '20px',
                        transform: 'translate(-50%, -50%)'
                      }}
                    >
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-20">
                        {item.submissions.toLocaleString()} submissions
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <div className="absolute bottom-0 left-0 right-0 flex justify-between">
                {weeklyActivity.map((item, idx) => (
                  <span key={idx} className="text-sm text-gray-600">{item.day}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Database Tables */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden mb-6">
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Database className="w-5 h-5 mr-2 text-indigo-600" />
              Database Tables
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Table</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Modified</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tableInfo.map((table, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`w-2 h-2 rounded-full mr-3 ${
                          table.status === 'optimal' ? 'bg-green-500' : 'bg-yellow-500'
                        } animate-pulse`}></div>
                        <span className="text-sm font-medium text-gray-900">{table.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {table.records.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{table.size}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {table.lastModified}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${
                        table.status === 'optimal' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {table.status === 'indexing' && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
                        {table.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button className="text-indigo-600 hover:text-indigo-700 font-medium">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivity.map((activity, idx) => {
              const Icon = activity.icon;
              return (
                <div key={idx} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <Icon className={`w-5 h-5 mt-0.5 ${activity.color}`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;