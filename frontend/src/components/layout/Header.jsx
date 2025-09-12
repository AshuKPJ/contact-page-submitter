// src/components/layout/Header.jsx - Enhanced Professional Version
import React, { useState, useEffect, useRef } from "react";
import { 
  User, LogOut, ChevronDown, LayoutDashboard, UserCircle, Rocket, 
  Settings, Activity, Bell, Search, HelpCircle, Menu, X, Zap,
  Shield, Users, BarChart3
} from "lucide-react";
import useAuth from "../../hooks/useAuth";
import { useNavigate, useLocation, Link } from "react-router-dom";

const Header = () => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(3);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const dropdownRef = useRef(null);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Navigation items based on user role
  const getNavItems = () => {
    if (!user) return [];
    
    const baseItems = [
      { 
        id: "dashboard",
        name: "Dashboard", 
        href: "/dashboard",
        icon: LayoutDashboard,
        description: "Overview & Analytics"
      },
      { 
        id: "activity",
        name: "Activity", 
        href: "/activity",
        icon: Activity,
        description: "Recent Activity"
      },
      { 
        id: "profile",
        name: "Contact Info", 
        href: "/contact-info",
        icon: UserCircle,
        description: "Your Information"
      }
    ];
    
    // Add campaign for regular users
    if (user.role === "user") {
      baseItems.splice(2, 0, { 
        id: "campaigns",
        name: "Campaigns", 
        href: "/campaigns",
        icon: Rocket,
        description: "Manage Campaigns"
      });
    }
    
    // Add admin panel for admins/owners
    if (user.role === "admin" || user.role === "owner") {
      baseItems.push({ 
        id: "admin",
        name: user.role === "owner" ? "Owner Panel" : "Admin Panel", 
        href: user.role === "owner" ? "/owner" : "/admin",
        icon: Shield,
        description: "System Management"
      });
    }
    
    return baseItems;
  };

  const navItems = getNavItems();

  // Check if a nav item is active
  const isActive = (href) => {
    if (href === '/dashboard' && location.pathname === '/') return true;
    return location.pathname.startsWith(href);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Quick actions for authenticated users
  const quickActions = [
    {
      icon: Search,
      label: "Search",
      action: () => console.log("Search clicked"),
      className: "text-gray-500 hover:text-gray-700"
    },
    {
      icon: Bell,
      label: "Notifications",
      action: () => console.log("Notifications clicked"),
      className: "text-gray-500 hover:text-gray-700",
      badge: notificationCount
    },
    {
      icon: HelpCircle,
      label: "Help",
      action: () => window.open("/help", "_blank"),
      className: "text-gray-500 hover:text-gray-700"
    }
  ];

  // Guest header (no user logged in)
  if (!user) {
    return (
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <img
                className="h-10 w-auto"
                alt="Contact Page Submitter"
                src="/assets/images/CPS_Header_Logo.png"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="hidden items-center space-x-2" style={{ display: 'none' }}>
                <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  CPS
                </span>
              </div>
            </Link>
            
            <div className="flex items-center space-x-4">
              <Link 
                to="/login" 
                className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-medium transition-all duration-200 shadow-sm hover:shadow-md"
              >
                Get Started
              </Link>
            </div>
          </div>
        </nav>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo Section */}
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center space-x-3 group">
              <img
                className="h-10 w-auto transition-transform group-hover:scale-105"
                alt="Contact Page Submitter"
                src="/assets/images/CPS_Header_Logo.png"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="hidden items-center space-x-2 group-hover:scale-105 transition-transform" style={{ display: 'none' }}>
                <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  CPS
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                
                return (
                  <Link
                    key={item.id}
                    to={item.href}
                    className={`group relative flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                      active 
                        ? 'bg-indigo-50 text-indigo-700 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className={`w-4 h-4 transition-colors ${
                      active ? 'text-indigo-600' : 'text-gray-500 group-hover:text-gray-700'
                    }`} />
                    <span>{item.name}</span>
                    {active && (
                      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                        <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full"></div>
                      </div>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Quick Actions - Desktop Only */}
            <div className="hidden md:flex items-center space-x-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <button
                    key={index}
                    onClick={action.action}
                    className={`relative p-2 rounded-lg transition-all duration-200 hover:bg-gray-100 ${action.className}`}
                    title={action.label}
                  >
                    <Icon className="w-5 h-5" />
                    {action.badge > 0 && (
                      <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                        {action.badge > 99 ? '99+' : action.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            {/* User Menu */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-3 px-3 py-2 rounded-xl hover:bg-gray-50 transition-all duration-200 border border-gray-200 hover:border-gray-300 shadow-sm hover:shadow-md group"
              >
                {/* User Avatar */}
                <div className="relative">
                  <div className="h-9 w-9 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center text-sm font-semibold shadow-sm">
                    {user.first_name?.[0]}{user.last_name?.[0]}
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                
                {/* User Info - Desktop Only */}
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-semibold text-gray-900 group-hover:text-gray-700">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
                
                <ChevronDown className={`h-4 w-4 text-gray-400 transition-all duration-200 group-hover:text-gray-600 ${
                  userMenuOpen ? "rotate-180" : ""
                }`} />
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50 animate-in slide-in-from-top-2 duration-200">
                  {/* User Header */}
                  <div className="px-6 py-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-100">
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <div className="h-12 w-12 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center font-semibold text-lg">
                          {user.first_name?.[0]}{user.last_name?.[0]}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {user.first_name} {user.last_name}
                        </p>
                        <p className="text-xs text-gray-600 truncate">{user.email}</p>
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 capitalize mt-1">
                          {user.role}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Menu Items */}
                  <div className="py-2">
                    <Link
                      to="/contact-info"
                      className="flex items-center space-x-3 px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <User className="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                      <div>
                        <span className="font-medium">Profile Settings</span>
                        <p className="text-xs text-gray-500">Update your information</p>
                      </div>
                    </Link>
                    
                    <Link
                      to="/activity"
                      className="flex items-center space-x-3 px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Activity className="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                      <div>
                        <span className="font-medium">Activity Log</span>
                        <p className="text-xs text-gray-500">View recent actions</p>
                      </div>
                    </Link>

                    {user.role === "user" && (
                      <Link
                        to="/campaigns"
                        className="flex items-center space-x-3 px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <Rocket className="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                        <div>
                          <span className="font-medium">My Campaigns</span>
                          <p className="text-xs text-gray-500">Manage your campaigns</p>
                        </div>
                      </Link>
                    )}

                    {(user.role === "admin" || user.role === "owner") && (
                      <Link
                        to={user.role === "owner" ? "/owner" : "/admin"}
                        className="flex items-center space-x-3 px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <Shield className="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                        <div>
                          <span className="font-medium">{user.role === "owner" ? "Owner" : "Admin"} Panel</span>
                          <p className="text-xs text-gray-500">System management</p>
                        </div>
                      </Link>
                    )}

                    <Link
                      to="/settings"
                      className="flex items-center space-x-3 px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Settings className="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                      <div>
                        <span className="font-medium">Settings</span>
                        <p className="text-xs text-gray-500">Preferences & security</p>
                      </div>
                    </Link>
                  </div>
                  
                  {/* Logout */}
                  <div className="border-t border-gray-100">
                    <button
                      onClick={() => {
                        handleLogout();
                        setUserMenuOpen(false);
                      }}
                      className="w-full flex items-center space-x-3 px-6 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors group"
                    >
                      <LogOut className="h-5 w-5 text-red-500" />
                      <div className="text-left">
                        <span className="font-medium">Sign Out</span>
                        <p className="text-xs text-red-400">End your session</p>
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 bg-white">
            <div className="px-4 py-4 space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                
                return (
                  <Link
                    key={item.id}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      active 
                        ? 'bg-indigo-50 text-indigo-700' 
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className={`h-5 w-5 ${
                      active ? 'text-indigo-600' : 'text-gray-500'
                    }`} />
                    <div className="flex-1">
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-500">{item.description}</div>
                    </div>
                  </Link>
                );
              })}
              
              {/* Mobile Quick Actions */}
              <div className="pt-4 border-t border-gray-200">
                <div className="grid grid-cols-3 gap-2">
                  {quickActions.map((action, index) => {
                    const Icon = action.icon;
                    return (
                      <button
                        key={index}
                        onClick={() => {
                          action.action();
                          setMobileMenuOpen(false);
                        }}
                        className="flex flex-col items-center space-y-2 p-3 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
                      >
                        <div className="relative">
                          <Icon className="w-6 h-6" />
                          {action.badge > 0 && (
                            <span className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                              {action.badge > 9 ? '9+' : action.badge}
                            </span>
                          )}
                        </div>
                        <span className="text-xs font-medium">{action.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;