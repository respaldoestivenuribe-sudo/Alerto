import React from 'react';
import { NavLink } from 'react-router-dom';
import { Droplets, AlertTriangle, FlaskConical, Bell, ShieldCheck } from 'lucide-react';
import { isAdmin } from '../utils/auth';
import './Sidebar.css';

const logoUrl = '/logo/Logo.png';

export const Sidebar = () => {
  const menuItems = [
    { path: '/precipitation', name: 'Precipitación', icon: Droplets },
    { path: '/risk',          name: 'Riesgo',        icon: AlertTriangle },
    { path: '/alerts',        name: 'Alertas',       icon: Bell },
    { path: '/simulator',     name: 'Simulador',     icon: FlaskConical },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-container">
          <img src={logoUrl} alt="Alerto" className="logo-img" />
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Menú principal">
        <ul className="nav-list">
          {menuItems.map((item) => (
            <li key={item.path} className="nav-item">
              <NavLink
                to={item.path}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                aria-current={undefined}
              >
                <item.icon size={20} className="nav-icon" aria-hidden="true" />
                <span>{item.name}</span>
              </NavLink>
            </li>
          ))}

          {isAdmin() && (
            <li className="nav-item nav-separator">
              <NavLink
                to="/admin"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <ShieldCheck size={20} className="nav-icon" aria-hidden="true" />
                <span>Administración</span>
              </NavLink>
            </li>
          )}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <div className="status-indicator online" aria-hidden="true"></div>
          <span>Sistema en línea</span>
        </div>
      </div>
    </aside>
  );
};
