// src/components/layout/Header.jsx
import React, { useState, useEffect } from "react";
import { 
  User, LogOut, ChevronDown, LayoutDashboard, 
  UserCircle, Rocket, Settings, Activity
} from "lucide-react";
import useAuth from "../../hooks/useAuth";
import { useNavigate, useLocation } from "react-router-dom";

const Header = () => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Navigation items based on user role
  const getNavItems = () => {
    if (!user) return [];
    
    const baseItems = [
      { 
        id: "dashboard",
        name: "Dashboard", 
        href: "/dashboard",
        icon: LayoutDashboard
      },
      { 
        id: "profile",
        name: "Contact Info", 
        href: "/ContactInformationForm",
        icon: UserCircle
      }
    ];
    
    // Only show "Start Campaign" for regular users
    if (user.role === "user") {
      baseItems.push({ 
        id: "campaign",
        name: "Start Campaign", 
        href: "/form-submitter",
        icon: Rocket
      });
    }
    
    return baseItems;
  };

  const navItems = getNavItems();

  // Check if a nav item is active based on current URL
  const isActive = (href) => {
    return location.pathname === href;
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  if (!user) {
    return (
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-blue-100 shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <a href="/" className="flex items-center">
              <img
                className="h-10 w-auto"
                alt="Contact Page Submitter"
                src="/assets/images/CPS_Header_Logo.png"
              />
            </a>
          </div>
        </nav>
      </header>
    );
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-blue-100 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <a href="/" className="flex items-center">
            <img
              className="h-10 w-auto"
              alt="Contact Page Submitter"
              src="/assets/images/CPS_Header_Logo.png"
            />
          </a>

          {/* Navigation Tabs */}
          <div className="hidden md:flex items-center">
            <div className="flex items-center space-x-2 bg-blue-50/50 rounded-full p-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                
                return (
                  <a
                    key={item.id}
                    href={item.href}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
                      active 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'text-blue-700 hover:bg-blue-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${
                      active ? 'text-white' : 'text-blue-600'
                    }`} />
                    <span className="font-medium text-sm">{item.name}</span>
                  </a>
                );
              })}
            </div>
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-blue-50 transition-all duration-200 border border-blue-200"
            >
              {/* User Avatar */}
              <div className="h-8 w-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-semibold">
                {user.first_name?.[0]}{user.last_name?.[0]}
              </div>
              
              {/* User Info */}
              <div className="hidden sm:block text-left">
                <p className="text-sm font-semibold text-gray-900">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-blue-600">{user.role}</p>
              </div>
              
              <ChevronDown className={`h-4 w-4 text-blue-600 transition-transform duration-200 ${
                userMenuOpen ? "rotate-180" : ""
              }`} />
            </button>

            {/* Dropdown Menu */}
            {userMenuOpen && (
              <>
                {/* Backdrop */}
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setUserMenuOpen(false)}
                ></div>
                
                {/* Menu */}
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-blue-100 overflow-hidden z-50">
                  {/* User Header */}
                  <div className="px-4 py-3 bg-blue-50 border-b border-blue-100">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
                        {user.first_name?.[0]}{user.last_name?.[0]}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">
                          {user.first_name} {user.last_name}
                        </p>
                        <p className="text-xs text-gray-600">{user.email}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Menu Items */}
                  <div className="py-1">
                    <a
                      href="/ContactInformationForm"
                      className="flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 transition-colors"
                    >
                      <User className="h-4 w-4 text-blue-600" />
                      <span>Profile Settings</span>
                    </a>
                    <a
                      href="/dashboard"
                      className="flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 transition-colors"
                    >
                      <Activity className="h-4 w-4 text-blue-600" />
                      <span>View Activity</span>
                    </a>
                    {(user.role === "admin" || user.role === "owner") && (
                      <a
                        href={user.role === "owner" ? "/owner" : "/admin"}
                        className="flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 transition-colors"
                      >
                        <Settings className="h-4 w-4 text-blue-600" />
                        <span>Admin Settings</span>
                      </a>
                    )}
                  </div>
                  
                  {/* Logout */}
                  <div className="border-t border-blue-100">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;