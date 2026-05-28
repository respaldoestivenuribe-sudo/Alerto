import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { Users, ShieldCheck, ToggleLeft, ToggleRight, Settings } from 'lucide-react';
import { authFetch } from '../utils/auth';
import './Admin.css';

const ROLE_OPTIONS = ['usuario', 'administrador'];

export const Admin = () => {
  const [users,   setUsers]   = useState([]);
  const [config,  setConfig]  = useState([]);
  const [tab,     setTab]     = useState('users');
  const [loading, setLoading] = useState(true);
  const [saving,  setSaving]  = useState(null);
  const [error,   setError]   = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [uRes, cRes] = await Promise.all([
          authFetch('/api/admin/users'),
          authFetch('/api/config'),
        ]);
        if (uRes.ok) setUsers(await uRes.json());
        if (cRes.ok) setConfig(await cRes.json());
      } catch {
        setError('Error al cargar datos.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const updateRole = async (id, role) => {
    setSaving(`role-${id}`);
    const res = await authFetch(`/api/admin/users/${id}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
    if (res.ok) setUsers((prev) => prev.map((u) => u.id === id ? { ...u, role } : u));
    setSaving(null);
  };

  const toggleStatus = async (id, current) => {
    setSaving(`status-${id}`);
    const res = await authFetch(`/api/admin/users/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !current }),
    });
    if (res.ok)
      setUsers((prev) => prev.map((u) => u.id === id ? { ...u, is_active: !current } : u));
    setSaving(null);
  };

  const updateConfig = async (key, value) => {
    setSaving(`cfg-${key}`);
    const res = await authFetch(`/api/config/${key}`, {
      method: 'PATCH',
      body: JSON.stringify({ value }),
    });
    if (res.ok)
      setConfig((prev) => prev.map((c) => c.key === key ? { ...c, value } : c));
    setSaving(null);
  };

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>Administración</h1>
          <p className="text-muted">Gestión de usuarios y configuración del sistema</p>
        </div>
      </div>

      {error && <p className="auth-error">{error}</p>}

      <div className="admin-tabs">
        <button className={`tab-btn ${tab === 'users' ? 'active' : ''}`}
          onClick={() => setTab('users')}>
          <Users size={16} /> Usuarios
        </button>
        <button className={`tab-btn ${tab === 'config' ? 'active' : ''}`}
          onClick={() => setTab('config')}>
          <Settings size={16} /> Configuración
        </button>
      </div>

      {tab === 'users' && (
        <Card title="Usuarios registrados">
          <div className="table-responsive">
            <table className="risk-table" aria-label="Gestión de usuarios">
              <thead>
                <tr>
                  <th scope="col">Nombre</th>
                  <th scope="col">Email</th>
                  <th scope="col">Rol</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Creado</th>
                  <th scope="col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="6" className="text-center">Cargando...</td></tr>
                ) : users.map((u) => (
                  <tr key={u.id}>
                    <td className="user-name">{u.nombre}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        className="role-select"
                        value={u.role}
                        disabled={saving === `role-${u.id}`}
                        onChange={(e) => updateRole(u.id, e.target.value)}
                        aria-label={`Rol de ${u.nombre}`}
                      >
                        {ROLE_OPTIONS.map((r) => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-success' : 'badge-inactive'}`}>
                        {u.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="text-muted">
                      {new Date(u.created_at).toLocaleDateString('es-ES')}
                    </td>
                    <td>
                      <button
                        className={`toggle-btn ${u.is_active ? 'active' : ''}`}
                        onClick={() => toggleStatus(u.id, u.is_active)}
                        disabled={saving === `status-${u.id}`}
                        aria-label={u.is_active ? `Desactivar ${u.nombre}` : `Activar ${u.nombre}`}
                        title={u.is_active ? 'Desactivar cuenta' : 'Activar cuenta'}
                      >
                        {u.is_active
                          ? <ToggleRight size={22} />
                          : <ToggleLeft size={22} />}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {tab === 'config' && (
        <Card title="Configuración del sistema (RF-005, RF-006)">
          <p className="config-note text-muted">
            Los cambios de umbral aplican en el próximo ciclo del pipeline.
          </p>
          <div className="config-grid">
            {config.map((c) => (
              <div key={c.key} className="config-item">
                <label className="form-label" htmlFor={`cfg-${c.key}`}>
                  {c.description ?? c.key}
                </label>
                <div className="config-input-row">
                  <input
                    id={`cfg-${c.key}`}
                    type="number"
                    className="form-input config-input"
                    defaultValue={c.value}
                    onBlur={(e) => {
                      if (e.target.value !== c.value)
                        updateConfig(c.key, e.target.value);
                    }}
                  />
                  {saving === `cfg-${c.key}` && (
                    <span className="config-saving">Guardando...</span>
                  )}
                </div>
                <span className="config-meta text-muted">
                  {c.updated_at
                    ? `Actualizado: ${new Date(c.updated_at).toLocaleString('es-ES')}`
                    : ''}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
