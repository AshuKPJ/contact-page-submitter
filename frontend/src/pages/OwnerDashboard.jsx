import React, { useState } from "react";
import { 
  DollarSign, Users, TrendingUp, UserPlus, CreditCard, Shield, Activity, 
  Settings, Mail, Globe, AlertCircle, CheckCircle, Clock, FileText, 
  ChevronDown, MoreVertical, Eye, Edit, Pause, Play, RefreshCw, Zap,
  BarChart3, Target, Calendar, Award, Briefcase, Send
} from "lucide-react";

const OwnerDashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("month");
  const [activeTab, setActiveTab] = useState("overview");
  
  // Enhanced stats
  const stats = [
    { 
      label: "Total Revenue", 
      value: "$48,200",
      change: "+21.1%",
      isPositive: true,
      icon: DollarSign,
      lightColor: "bg-green-100",
      iconColor: "text-green-600",
      description: "This month"
    },
    { 
      label: "Active Users", 
      value: "132",
      change: "+15.8%",
      isPositive: true,
      icon: Users,
      lightColor: "bg-blue-100",
      iconColor: "text-blue-600",
      description: "Paid accounts"
    },
    { 
      label: "New Signups", 
      value: "41",
      change: "+41.4%",
      isPositive: true,
      icon: UserPlus,
      lightColor: "bg-purple-100",
      iconColor: "text-purple-600",
      description: "Last 30 days"
    },
    { 
      label: "Success Rate", 
      value: "96.8%",
      change: "+2.3%",
      isPositive: true,
      icon: Target,
      lightColor: "bg-orange-100",
      iconColor: "text-orange-600",
      description: "Average rate"
    },
  ];

  // Revenue data
  const revenueData = [
    { month: 'Jan', revenue: 35000, users: 98 },
    { month: 'Feb', revenue: 38000, users: 105 },
    { month: 'Mar', revenue: 41000, users: 112 },
    { month: 'Apr', revenue: 43000, users: 118 },
    { month: 'May', revenue: 48200, users: 132 },
  ];

  // Subscription distribution
  const subscriptionData = [
    { label: "Professional", value: 78, color: "#10B981", percentage: 59 },
    { label: "Business", value: 42, color: "#F59E0B", percentage: 32 },
    { label: "Enterprise", value: 12, color: "#EF4444", percentage: 9 },
  ];

  // Team members
  const teamMembers = [
    {
      id: 1,
      name: "Tom Mack",
      email: "tom@example.com",
      role: "Admin",
      region: "East Region",
      status: "Active",
      lastActive: "2 min ago",
      customers: 45,
      revenue: "$12,400",
      performance: 98
    },
    {
      id: 2,
      name: "Kim Gregory",
      email: "kim@example.com",
      role: "Admin",
      region: "Marketing",
      status: "Active",
      lastActive: "1 hour ago",
      customers: 38,
      revenue: "$9,800",
      performance: 92
    },
    {
      id: 3,
      name: "Lisa Chen",
      email: "lisa@example.com",
      role: "Admin",
      region: "West Region",
      status: "Active",
      lastActive: "30 min ago",
      customers: 52,
      revenue: "$14,200",
      performance: 96
    },
  ];

  // Customer activity
  const customerActivity = [
    { hour: '00:00', submissions: 120 },
    { hour: '04:00', submissions: 85 },
    { hour: '08:00', submissions: 245 },
    { hour: '12:00', submissions: 380 },
    { hour: '16:00', submissions: 425 },
    { hour: '20:00', submissions: 310 },
  ];

  // System metrics
  const systemMetrics = {
    totalCampaigns: 1847,
    activeCSVs: 23,
    avgSuccessRate: 96.8,
    totalSubmissions: "2.4M",
    serverLoad: 67
  };

  // Recent transactions
  const recentTransactions = [
    { id: 1, customer: "Acme Corp", plan: "Professional", amount: "$149", date: "Today", status: "success" },
    { id: 2, customer: "Tech Solutions", plan: "Business", amount: "$299", date: "Yesterday", status: "success" },
    { id: 3, customer: "StartupXYZ", plan: "Professional", amount: "$149", date: "2 days ago", status: "pending" },
    { id: 4, customer: "Global Inc", plan: "Enterprise", amount: "$599", date: "3 days ago", status: "success" },
  ];

  const maxRevenue = Math.max(...revenueData.map(d => d.revenue));
  const maxActivity = Math.max(...customerActivity.map(d => d.submissions));

  // Donut chart calculation
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

  const donutTotal = subscriptionData.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -90;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Owner Dashboard</h1>
              <p className="text-gray-600">Business overview and team management</p>
            </div>
            <div className="flex items-center space-x-3">
              <select 
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* System Health Bar */}
        <div className="bg-green-500 rounded-lg p-4 mb-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
              <span className="font-semibold">System Status: All Services Operational</span>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>Load: {systemMetrics.serverLoad}%</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>{systemMetrics.activeCSVs} Active CSVs</span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span>{systemMetrics.avgSuccessRate}% Success</span>
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
                    stat.isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <TrendingUp className={`w-3 h-3 mr-1 ${!stat.isPositive && 'rotate-180'}`} />
                    {stat.change}
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
          {/* Revenue Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-purple-600" />
              Revenue Growth
            </h3>
            <div className="relative h-64">
              <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
                <span>$50K</span>
                <span>$40K</span>
                <span>$30K</span>
                <span>$20K</span>
                <span>$10K</span>
              </div>
              
              <div className="ml-12 h-full pb-8 relative">
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-gray-200"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-200"></div>
                </div>
                
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 380 200">
                  <defs>
                    <linearGradient id="revenueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#A855F7" stopOpacity="0.3" />
                      <stop offset="100%" stopColor="#A855F7" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  
                  {(() => {
                    const chartWidth = 380;
                    const chartHeight = 200;
                    const points = revenueData.map((item, idx) => {
                      const x = (idx / (revenueData.length - 1)) * chartWidth;
                      const y = chartHeight - (item.revenue / 50000) * chartHeight;
                      return `${x},${y}`;
                    });
                    
                    const areaPath = `M ${points[0]} L ${points.join(' L ')} L ${chartWidth},${chartHeight} L 0,${chartHeight} Z`;
                    
                    return (
                      <>
                        <path d={areaPath} fill="url(#revenueGradient)" />
                        <polyline
                          points={points.join(' ')}
                          fill="none"
                          stroke="#A855F7"
                          strokeWidth="3"
                          strokeLinejoin="round"
                          strokeLinecap="round"
                        />
                        {revenueData.map((item, idx) => {
                          const x = (idx / (revenueData.length - 1)) * chartWidth;
                          const y = chartHeight - (item.revenue / 50000) * chartHeight;
                          return (
                            <circle key={idx} cx={x} cy={y} r="5" fill="white" stroke="#A855F7" strokeWidth="3" />
                          );
                        })}
                      </>
                    );
                  })()}
                </svg>
                
                <div className="absolute bottom-0 left-0 right-0 flex justify-between">
                  {revenueData.map((item, idx) => (
                    <span key={idx} className="text-sm text-gray-600">{item.month}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Subscription Distribution */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Award className="w-5 h-5 mr-2 text-purple-600" />
              Plan Distribution
            </h3>
            <div className="flex items-center justify-around">
              <div className="relative">
                <svg width="170" height="170" className="transform -rotate-90">
                  {subscriptionData.map((item, idx) => {
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
                    <p className="text-3xl font-bold text-gray-900">{donutTotal}</p>
                    <p className="text-sm text-gray-500">Users</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                {subscriptionData.map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-3">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{item.label}</p>
                      <p className="text-xs text-gray-500">{item.percentage}% • {item.value} users</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Customer Activity Chart */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-purple-600" />
            Customer Activity (24h)
          </h3>
          <div className="relative h-48">
            <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
              <span>500</span>
              <span>400</span>
              <span>300</span>
              <span>200</span>
              <span>100</span>
              <span>0</span>
            </div>
            
            <div className="ml-10 h-full pb-8 relative">
              <div className="absolute inset-0 flex flex-col justify-between">
                <div className="border-t border-gray-200"></div>
                <div className="border-t border-gray-100"></div>
                <div className="border-t border-gray-100"></div>
                <div className="border-t border-gray-100"></div>
                <div className="border-t border-gray-100"></div>
                <div className="border-t border-gray-200"></div>
              </div>
              
              <div className="relative h-full flex items-end justify-around">
                {customerActivity.map((item, idx) => (
                  <div key={idx} className="flex-1 flex flex-col items-center mx-2 group">
                    <div className="relative w-full flex justify-center">
                      <div 
                        className="w-12 bg-gradient-to-t from-purple-600 to-purple-400 rounded-t hover:from-purple-700 hover:to-purple-500 transition-all cursor-pointer shadow-sm"
                        style={{ 
                          height: `${(item.submissions / 500) * 160}px`
                        }}
                      >
                        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                          {item.submissions} submissions
                        </div>
                      </div>
                    </div>
                    <span className="text-sm text-gray-600 mt-2">{item.hour}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Team Members Table */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden mb-6">
          <div className="px-6 py-4 bg-gray-50 border-b flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Users className="w-5 h-5 mr-2 text-purple-600" />
              Team Performance
            </h3>
            <button className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors">
              Add Member
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Member</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customers</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {teamMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-semibold">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{member.name}</div>
                          <div className="text-xs text-gray-500">{member.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{member.role}</div>
                      <div className="text-xs text-gray-500">{member.region}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {member.customers}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {member.revenue}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">{member.performance}%</span>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              member.performance >= 95 ? 'bg-green-500' : 
                              member.performance >= 90 ? 'bg-blue-500' : 'bg-yellow-500'
                            }`}
                            style={{ width: `${member.performance}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-1.5"></span>
                        {member.status}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{member.lastActive}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center space-x-2">
                        <button className="text-purple-600 hover:text-purple-700">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700">
                          <Edit className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CreditCard className="w-5 h-5 mr-2 text-purple-600" />
            Recent Transactions
          </h3>
          <div className="space-y-3">
            {recentTransactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    transaction.status === 'success' ? 'bg-green-500' : 'bg-yellow-500'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{transaction.customer}</p>
                    <p className="text-xs text-gray-500">{transaction.plan} Plan • {transaction.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-gray-900">{transaction.amount}</p>
                  <p className={`text-xs ${
                    transaction.status === 'success' ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {transaction.status}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OwnerDashboard;