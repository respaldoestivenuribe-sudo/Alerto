import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LogOut, Bell, User, AlertTriangle } from 'lucide-react';
import { getUser, clearAuth, authFetch, isAdmin } from '../utils/auth';
import './Topbar.css';

const PAGE_TITLES = {
  '/precipitation': 'Precipitación',
  '/risk':          'Riesgo',
  '/simulator':     'Simulador',
  '/alerts':        'Alertas',
  '/admin':         'Administración',
};

const ROLE_LABELS = {
  administrador: 'Administrador',
  usuario:       'Usuario',
};

const RISK_COLORS = { ROJO: '#ef4444', NARANJA: '#f97316' };

export const Topbar = () => {
  const navigate  = useNavigate();
  const location  = useLocation();
  const user      = getUser();
  const dropRef   = useRef(null);

  const [alerts,    setAlerts]    = useState([]);
  const [showDrop,  setShowDrop]  = useState(false);

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'Sistema de Monitoreo';

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await authFetch('/api/risk/alerts/recent?hours=24');
        if (res.ok) setAlerts(await res.json());
      } catch {
        // non-critical — keep previous state
      }
    };
    fetchAlerts();
    const id = setInterval(fetchAlerts, 60_000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const handleClick = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setShowDrop(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h2 className="page-title">{pageTitle}</h2>
      </div>

      <div className="topbar-right">
        {/* ── Notification bell ──────────────────────────────── */}
        <div className="notif-wrapper" ref={dropRef}>
          <button
            className="icon-btn"
            aria-label={`Notificaciones (${alerts.length})`}
            onClick={() => setShowDrop((v) => !v)}
          >
            <Bell size={20} />
            {alerts.length > 0 && (
              <span className="notification-badge">
                {alerts.length > 9 ? '9+' : alerts.length}
              </span>
            )}
          </button>

          {showDrop && (
            <div className="notif-dropdown" role="menu">
              <p className="notif-header">Alertas últimas 24h</p>
              {alerts.length === 0 ? (
                <p className="notif-empty">Sin alertas críticas</p>
              ) : (
                alerts.slice(0, 8).map((a) => (
                  <div key={a.id} className="notif-item">
                    <AlertTriangle size={14}
                      style={{ color: RISK_COLORS[a.nivel_riesgo] ?? '#f97316' }} />
                    <div className="notif-text">
                      <span className="notif-level"
                        style={{ color: RISK_COLORS[a.nivel_riesgo] ?? '#f97316' }}>
                        {a.nivel_riesgo}
                      </span>
                      <span className="notif-time">
                        {new Date(a.evaluated_at).toLocaleString('es-ES', {
                          hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short'
                        })}
                      </span>
                    </div>
                  </div>
                ))
              )}
              <button className="notif-footer-btn"
                onClick={() => { setShowDrop(false); navigate('/alerts'); }}>
                Ver todas las alertas
              </button>
            </div>
          )}
        </div>

        {/* ── User info ──────────────────────────────────────── */}
        <div className="user-profile">
          <div className="avatar" aria-hidden="true">
            <User size={18} />
          </div>
          <div className="user-info">
            <span className="greeting">Hola, {user?.name ?? 'Usuario'}</span>
            <span className="role">{ROLE_LABELS[user?.role] ?? 'Usuario'}</span>
          </div>
        </div>

        <button className="btn-outline logout-btn" onClick={handleLogout}
          aria-label="Cerrar sesión">
          <LogOut size={18} />
          <span>Salir</span>
        </button>
      </div>
    </header>
  );
};
