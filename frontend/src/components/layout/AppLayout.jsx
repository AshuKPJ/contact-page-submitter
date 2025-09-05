// src/components/layout/AppLayout.jsx
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navigation from '../Navigation';
import useAuth from '../../hooks/useAuth';

const AppLayout = () => {
  const { user } = useAuth();
  const location = useLocation();

  // Show navigation for authenticated users, except on landing page
  const showNavigation = user && location.pathname !== '/';

  return (
    <div className="min-h-screen bg-gray-50">
      {showNavigation && <Navigation />}
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;