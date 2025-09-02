// src/pages/UserDashboard.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Play, CheckCircle, Clock, Mail, Globe, 
  AlertCircle, Upload, FileText, TrendingUp, BarChart3, Activity, Target
} from "lucide-react";

const UserDashboard = () => {
  const navigate = useNavigate();
  const [campaignRunning, setCampaignRunning] = useState(false); // Set to false by default

  // Current campaign data (if running)
  const currentCampaign = campaignRunning ? {
    fileName: "tech_companies_list.csv",
    totalWebsites: 2400,
    processed: 1392,
    successful: 1348,
    failed: 44,
    startTime: "10:15 AM",
    estimatedEnd: "1:45 PM"
  } : null;

  // Analytics data
  const stats = {
    totalSubmitted: 2345,
    captchaFailed: 45,
    noContactPage: 67,
    successfulSubmissions: 2233
  };

  // Monthly submissions data for bar chart
  const monthlyData = [
    { month: 'Jan', count: 340 },
    { month: 'Feb', count: 520 },
    { month: 'Mar', count: 680 },
    { month: 'Apr', count: 450 },
    { month: 'May', count: 780 },
  ];

  // Weekly activity data for line chart
  const weeklyData = [
    { day: 'Mon', count: 180 },
    { day: 'Tue', count: 420 },
    { day: 'Wed', count: 280 },
    { day: 'Thu', count: 480 },
    { day: 'Fri', count: 620 },
    { day: 'Sat', count: 580 },
    { day: 'Sun', count: 380 },
  ];

  // Pie chart data
  const submissionResults = [
    { label: 'Successful', value: 2233, color: '#10B981', percentage: 87 },
    { label: 'Email Fallback', value: 67, color: '#F59E0B', percentage: 7 },
    { label: 'Failed', value: 45, color: '#EF4444', percentage: 6 },
  ];

  const handleNewCampaign = () => {
    navigate('/form-submitter');
  };

  // Calculate max value for bar chart scaling
  const maxMonthlyValue = Math.max(...monthlyData.map(d => d.count));
  const maxWeeklyValue = Math.max(...weeklyData.map(d => d.count));

  // Create donut chart paths
  const createDonutPath = (value, total, startAngle, color) => {
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

  // Calculate total for donut chart
  const donutTotal = submissionResults.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -90; // Start from top

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Simple Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor your campaigns and performance</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Current Campaign Status */}
        {currentCampaign ? (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                  <Play className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Campaign Running
                  </h2>
                  <p className="text-sm text-gray-500">
                    File: {currentCampaign.fileName}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Processing</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">
                  Progress: {currentCampaign.processed} of {currentCampaign.totalWebsites} websites
                </span>
                <span className="font-medium text-gray-900">
                  {Math.round((currentCampaign.processed / currentCampaign.totalWebsites) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-green-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(currentCampaign.processed / currentCampaign.totalWebsites) * 100}%` }}
                />
              </div>
            </div>

            {/* Campaign Stats */}
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{currentCampaign.successful}</p>
                <p className="text-xs text-gray-500">Successful</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{currentCampaign.failed}</p>
                <p className="text-xs text-gray-500">Failed</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {Math.round((currentCampaign.successful / currentCampaign.processed) * 100)}%
                </p>
                <p className="text-xs text-gray-500">Success Rate</p>
              </div>
            </div>

            {/* Time Info */}
            <div className="flex items-center justify-between text-sm text-gray-600 pt-4 border-t">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>Started: {currentCampaign.startTime}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>Estimated completion: {currentCampaign.estimatedEnd}</span>
              </div>
            </div>
          </div>
        ) : (
          /* Campaign Status and Quick Actions */
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Status Card */}
              <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Campaign Status</h2>
                    <p className="text-sm text-gray-500">Ready to start a new campaign</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                    <span className="text-sm text-gray-600">Idle</span>
                  </div>
                </div>
                
                {/* Last Campaign Info */}
                <div className="p-4 bg-gray-50 rounded-lg mb-4">
                  <p className="text-xs text-gray-500 mb-2">LAST CAMPAIGN</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-2xl font-bold text-gray-900">1,847</p>
                      <p className="text-xs text-gray-500">Websites Processed</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">96.3%</p>
                      <p className="text-xs text-gray-500">Success Rate</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">15.4h</p>
                      <p className="text-xs text-gray-500">Duration</p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400 mt-3">Completed 2 days ago</p>
                </div>
                
                {/* Quick Actions */}
                <div className="flex space-x-3">
                  <button
                    onClick={handleNewCampaign}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center space-x-2"
                  >
                    <Upload className="w-4 h-4" />
                    <span>Start New Campaign</span>
                  </button>
                  <button
                    onClick={() => navigate('/ContactInformationForm')}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Update Contact Info
                  </button>
                </div>
              </div>
              
              {/* Performance Summary */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Avg Success Rate</span>
                      <span className="font-semibold">94.3%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: '94.3%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Form Fill Rate</span>
                      <span className="font-semibold">87%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: '87%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Email Fallback</span>
                      <span className="font-semibold">7%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '7%' }}></div>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500">Based on last 30 days</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Total Submitted</p>
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.totalSubmitted.toLocaleString()}</p>
            <div className="mt-2 flex items-center text-xs text-green-600">
              <TrendingUp className="w-3 h-3 mr-1" />
              <span>+12% from last month</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Captcha Failed</p>
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-3xl font-bold text-red-600">{stats.captchaFailed}</p>
            <p className="text-xs text-gray-500 mt-2">Configure Death By Captcha</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">No Contact Page</p>
              <Mail className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-3xl font-bold text-yellow-600">{stats.noContactPage}</p>
            <p className="text-xs text-gray-500 mt-2">Used email fallback</p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Monthly Submissions Bar Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
              Monthly Submissions
            </h3>
            <div className="relative h-64">
              {/* Y-axis labels */}
              <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
                <span>{Math.round(maxMonthlyValue)}</span>
                <span>{Math.round(maxMonthlyValue * 0.75)}</span>
                <span>{Math.round(maxMonthlyValue * 0.5)}</span>
                <span>{Math.round(maxMonthlyValue * 0.25)}</span>
                <span>0</span>
              </div>
              
              {/* Chart area */}
              <div className="ml-10 h-full pb-8 relative">
                {/* Grid lines */}
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-gray-200"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-100"></div>
                  <div className="border-t border-gray-200"></div>
                </div>
                
                {/* Bars */}
                <div className="relative h-full flex items-end justify-around">
                  {monthlyData.map((item, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center mx-2 group">
                      <div className="relative w-full flex justify-center">
                        <div 
                          className="w-12 bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t hover:from-indigo-700 hover:to-indigo-500 transition-all cursor-pointer shadow-sm"
                          style={{ 
                            height: `${(item.count / maxMonthlyValue) * 192}px`
                          }}
                        >
                          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                            {item.count} submissions
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

          {/* Submission Results Donut Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-indigo-600" />
              Submission Results
            </h3>
            <div className="flex items-center justify-around">
              <div className="relative">
                <svg width="170" height="170" className="transform -rotate-90">
                  {submissionResults.map((item, idx) => {
                    const path = createDonutPath(item.value, donutTotal, currentAngle, item.color);
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
                    <p className="text-3xl font-bold text-gray-900">{donutTotal.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Total</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                {submissionResults.map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-3">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{item.label}</p>
                      <p className="text-xs text-gray-500">{item.percentage}% • {item.value.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Activity Line Chart */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-indigo-600" />
            Weekly Activity
          </h3>
          <div className="relative h-64">
            {/* Y-axis labels */}
            <div className="absolute left-0 h-full flex flex-col justify-between pb-8 text-xs text-gray-500">
              <span>800</span>
              <span>600</span>
              <span>400</span>
              <span>200</span>
              <span>0</span>
            </div>
            
            {/* Chart area */}
            <div className="ml-10 h-full pb-8 relative">
              {/* Background grid */}
              <div className="absolute inset-0">
                <div className="h-full flex flex-col justify-between">
                  <div className="border-t border-gray-200"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-100 border-dashed"></div>
                  <div className="border-t border-gray-200"></div>
                </div>
              </div>
              
              {/* SVG Chart with fixed viewBox */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 420 200">
                {/* Area gradient definition */}
                <defs>
                  <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#818CF8" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="#818CF8" stopOpacity="0" />
                  </linearGradient>
                </defs>
                
                {/* Calculate actual pixel positions */}
                {(() => {
                  const chartWidth = 420;
                  const chartHeight = 200;
                  const points = weeklyData.map((item, idx) => {
                    const x = (idx / (weeklyData.length - 1)) * chartWidth;
                    const y = chartHeight - (item.count / 800) * chartHeight;
                    return `${x},${y}`;
                  });
                  
                  // Create area path
                  const areaPath = `M ${points[0]} L ${points.join(' L ')} L ${chartWidth},${chartHeight} L 0,${chartHeight} Z`;
                  
                  return (
                    <>
                      {/* Area fill */}
                      <path
                        d={areaPath}
                        fill="url(#lineGradient)"
                      />
                      
                      {/* Main line */}
                      <polyline
                        points={points.join(' ')}
                        fill="none"
                        stroke="#818CF8"
                        strokeWidth="3"
                        strokeLinejoin="round"
                        strokeLinecap="round"
                      />
                      
                      {/* Data points */}
                      {weeklyData.map((item, idx) => {
                        const x = (idx / (weeklyData.length - 1)) * chartWidth;
                        const y = chartHeight - (item.count / 800) * chartHeight;
                        return (
                          <g key={idx}>
                            <circle
                              cx={x}
                              cy={y}
                              r="5"
                              fill="white"
                              stroke="#818CF8"
                              strokeWidth="3"
                            />
                            <circle
                              cx={x}
                              cy={y}
                              r="12"
                              fill="transparent"
                              className="hover:fill-indigo-100 hover:fill-opacity-50 cursor-pointer"
                            />
                          </g>
                        );
                      })}
                    </>
                  );
                })()}
              </svg>
              
              {/* Hover tooltips */}
              <div className="absolute inset-0">
                {weeklyData.map((item, idx) => {
                  const x = (idx / (weeklyData.length - 1)) * 100;
                  const y = 100 - (item.count / 800) * 100;
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
                        {item.count} submissions
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* X-axis labels */}
              <div className="absolute bottom-0 left-0 right-0 flex justify-between">
                {weeklyData.map((item, idx) => (
                  <span key={idx} className="text-sm text-gray-600">{item.day}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Message sent to techcorp.com</p>
                <p className="text-xs text-gray-500">Contact form found and used • 2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <Mail className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Email sent to info@startup.io</p>
                <p className="text-xs text-gray-500">No form found, used email instead • 3 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Failed: nocontact.com</p>
                <p className="text-xs text-gray-500">No contact method found • 7 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Message sent to innovate.tech</p>
                <p className="text-xs text-gray-500">Contact form found and used • 8 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Message sent to webdev.io</p>
                <p className="text-xs text-gray-500">Contact form found and used • 10 minutes ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;