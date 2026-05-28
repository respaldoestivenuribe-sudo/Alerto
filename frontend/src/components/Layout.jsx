import React from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const Layout = () => {
  const location = useLocation();

  // Redirect root to dashboard
  if (location.pathname === '/') {
    return <Navigate to="/precipitation" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
