// src/components/layout/AppLayout.jsx - Enhanced Complete Version
import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate, Link } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import UserMenu from '../UserMenu';
import { 
  BarChart3, FileText, Rocket, Settings, Activity, Users, 
  Shield, ChevronRight, Menu, X, Home, LogOut, Bell,
  Plus, Search, HelpCircle, Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

const AppLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Get navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [
      {
        name: 'Dashboard',
        href: '/dashboard',
        icon: Home,
        description: 'Overview and stats'
      },
      {
        name: 'Campaigns',
        href: '/campaigns',
        icon: Rocket,
        description: 'Manage campaigns',
        badge: user?.activeCampaigns || 0
      },
      {
        name: 'Activity',
        href: '/activity',
        icon: Activity,
        description: 'Recent activity'
      },
      {
        name: 'Contact Info',
        href: '/contact-info',
        icon: Users,
        description: 'Your information'
      },
    ];

    // Add admin-specific items
    if (user?.role === 'admin' || user?.role === 'owner') {
      baseItems.push({
        name: 'Admin Panel',
        href: user.role === 'owner' ? '/owner' : '/admin',
        icon: Shield,
        description: 'System management'
      });
    }

    baseItems.push({
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'Preferences'
    });

    return baseItems;
  };

  const navigationItems = user ? getNavigationItems() : [];

  // Check if current path is active
  const isActive = (href) => {
    if (href === '/dashboard' && location.pathname === '/') return true;
    return location.pathname.startsWith(href);
  };

  // Quick actions
  const quickActions = [
    {
      label: 'New Campaign',
      icon: Plus,
      action: () => navigate('/campaigns/new'),
      color: 'text-indigo-600'
    },
    {
      label: 'View Activity',
      icon: Activity,
      action: () => navigate('/activity'),
      color: 'text-green-600'
    },
    {
      label: 'Help',
      icon: HelpCircle,
      action: () => toast.info('Help documentation coming soon!'),
      color: 'text-blue-600'
    }
  ];

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/');
  };

  // Don't show navigation on landing page or if not authenticated
  const showNavigation = user && location.pathname !== '/';

  if (!showNavigation) {
    return <Outlet />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 fixed top-0 w-full z-40">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Left side */}
            <div className="flex items-center">
              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-md text-gray-500 hover:bg-gray-100"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>

              {/* Logo */}
              <Link to="/dashboard" className="flex items-center ml-4 md:ml-0">
                <img
                  className="h-8 w-auto"
                  src="/assets/images/CPS_Header_Logo.png"
                  alt="CPS"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="hidden items-center" style={{ display: 'none' }}>
                  <Zap className="w-8 h-8 text-indigo-600" />
                  <span className="ml-2 text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    CPS
                  </span>
                </div>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:flex md:ml-10 md:space-x-1">
                {navigationItems.slice(0, 4).map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`group inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all ${
                        active
                          ? 'bg-indigo-50 text-indigo-700'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <Icon className={`w-4 h-4 mr-2 ${
                        active ? 'text-indigo-600' : 'text-gray-500 group-hover:text-gray-700'
                      }`} />
                      {item.name}
                      {item.badge > 0 && (
                        <span className="ml-2 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-3">
              {/* Search */}
              <button className="hidden lg:block p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                <Search className="w-5 h-5" />
              </button>

              {/* Notifications */}
              <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                <Bell className="w-5 h-5" />
                {notificationCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>

              {/* Quick Actions */}
              <div className="hidden lg:flex items-center space-x-1">
                {quickActions.map((action, idx) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={idx}
                      onClick={action.action}
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
                      title={action.label}
                    >
                      <Icon className={`w-5 h-5 ${action.color}`} />
                    </button>
                  );
                })}
              </div>

              {/* User Menu */}
              <UserMenu
                firstName={user?.first_name}
                lastName={user?.last_name}
                role={user?.role}
                email={user?.email}
                onLogout={handleLogout}
                enhanced={true}
              />
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium ${
                      active
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className={`w-5 h-5 mr-3 ${
                      active ? 'text-indigo-600' : 'text-gray-500'
                    }`} />
                    <div className="flex-1">
                      <div className="flex items-center">
                        {item.name}
                        {item.badge > 0 && (
                          <span className="ml-2 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full">
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                    </div>
                  </Link>
                );
              })}
              
              <hr className="my-2 border-gray-200" />
              
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50"
              >
                <LogOut className="w-5 h-5 mr-3" />
                Logout
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Desktop Sidebar (Optional - can be toggled) */}
      {sidebarOpen && (
        <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 lg:pt-16 bg-white border-r border-gray-200">
          <div className="flex-1 flex flex-col overflow-y-auto">
            <nav className="flex-1 px-4 py-4 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                      active
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className={`mr-3 h-5 w-5 ${
                      active ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                    }`} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        {item.name}
                        {item.badge > 0 && (
                          <span className="bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full">
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                    </div>
                    {active && <ChevronRight className="w-4 h-4 text-indigo-600" />}
                  </Link>
                );
              })}
            </nav>

            {/* Quick Stats */}
            <div className="p-4 border-t border-gray-200">
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-4 text-white">
                <h3 className="font-semibold mb-2">Quick Stats</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-indigo-100">Active Campaigns</span>
                    <span className="font-bold">{user?.activeCampaigns || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-100">Success Rate</span>
                    <span className="font-bold">{user?.successRate || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-100">Total Processed</span>
                    <span className="font-bold">{user?.totalProcessed || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      )}

      {/* Main Content Area */}
      <main className={`${sidebarOpen ? 'lg:pl-64' : ''} pt-16`}>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className={`${sidebarOpen ? 'lg:pl-64' : ''} bg-gradient-to-br from-gray-800 to-gray-900 text-gray-300 mt-auto`}>
        <div className="mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center space-y-4">
            {/* Footer Logo */}
            <img
              className="h-12 opacity-90"
              src="/assets/images/CPS_footer_logo.png"
              alt="Contact Page Submitter"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="hidden text-center" style={{ display: 'none' }}>
              <p className="text-xl font-bold text-gray-100">Contact Page Submitter</p>
            </div>
            
            <p className="text-center text-gray-400 max-w-2xl">
              AI automated personalized messages at scale!
            </p>
            
            <div className="flex items-center justify-between w-full pt-4 border-t border-gray-700">
              <p className="text-sm text-gray-500">
                © {new Date().getFullYear()} Contact Page Submitter. All rights reserved.
              </p>
              <div className="flex items-center space-x-4">
                <a href="#" className="text-sm text-gray-400 hover:text-gray-200 transition-colors">Privacy</a>
                <a href="#" className="text-sm text-gray-400 hover:text-gray-200 transition-colors">Terms</a>
                <a href="#" className="text-sm text-gray-400 hover:text-gray-200 transition-colors">Support</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;