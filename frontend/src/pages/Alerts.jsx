import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { AlertTriangle, Filter } from 'lucide-react';
import { authFetch } from '../utils/auth';
import './Alerts.css';

const LEVELS = ['TODOS', 'ROJO', 'NARANJA', 'AMARILLO', 'VERDE'];

const BADGE = {
  ROJO:     'badge-danger',
  NARANJA:  'badge-naranja',
  AMARILLO: 'badge-warning',
  VERDE:    'badge-success',
};

export const Alerts = () => {
  const [history, setHistory] = useState([]);
  const [filter,  setFilter]  = useState('TODOS');
  const [page,    setPage]    = useState(0);
  const [loading, setLoading] = useState(true);
  const PAGE_SIZE = 50;

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const res = await authFetch(
          `/api/risk/history?limit=${PAGE_SIZE}&offset=${page * PAGE_SIZE}`
        );
        if (res.ok) setHistory(await res.json());
      } catch (err) {
        console.error('Error fetching alerts:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [page]);

  const filtered = filter === 'TODOS'
    ? history
    : history.filter((r) => r.nivel_riesgo === filter);

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>Alertas</h1>
          <p className="text-muted">Historial de evaluaciones de riesgo</p>
        </div>
      </div>

      {/* Stats strip */}
      <div className="alert-stats">
        {['ROJO', 'NARANJA', 'AMARILLO', 'VERDE'].map((lvl) => (
          <div key={lvl} className={`alert-stat-card alert-stat-${lvl.toLowerCase()}`}>
            <AlertTriangle size={18} />
            <span className="alert-stat-count">
              {history.filter((r) => r.nivel_riesgo === lvl).length}
            </span>
            <span className="alert-stat-label">{lvl}</span>
          </div>
        ))}
      </div>

      <Card>
        {/* Filter bar */}
        <div className="filter-bar">
          <Filter size={16} className="filter-icon" />
          {LEVELS.map((lvl) => (
            <button
              key={lvl}
              className={`filter-btn ${filter === lvl ? 'active' : ''}`}
              onClick={() => setFilter(lvl)}
            >
              {lvl}
            </button>
          ))}
        </div>

        <div className="table-responsive">
          <table className="risk-table" aria-label="Historial de alertas">
            <thead>
              <tr>
                <th scope="col">Fecha y hora</th>
                <th scope="col">Nivel</th>
                <th scope="col">Score</th>
                <th scope="col">Precip. 1h</th>
                <th scope="col">Precip. 3h</th>
                <th scope="col">Humedad 6h</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="text-center">Cargando...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan="6" className="text-center">Sin registros.</td></tr>
              ) : (
                filtered.map((item, i) => (
                  <tr key={i} className={`row-${item.nivel_riesgo?.toLowerCase()}`}>
                    <td>{new Date(item.evaluated_at).toLocaleString('es-ES')}</td>
                    <td>
                      <span className={`badge ${BADGE[item.nivel_riesgo] ?? ''}`}>
                        {item.nivel_riesgo}
                      </span>
                    </td>
                    <td>{parseFloat(item.riesgo_score).toFixed(0)}%</td>
                    <td>{parseFloat(item.precip_1h ?? 0).toFixed(1)} mm</td>
                    <td>{parseFloat(item.precip_3h ?? 0).toFixed(1)} mm</td>
                    <td>{parseFloat(item.humedad_prom_6h ?? 0).toFixed(0)}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="pagination">
          <button className="btn-outline" disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}>
            Anterior
          </button>
          <span className="page-label">Página {page + 1}</span>
          <button className="btn-outline" disabled={history.length < PAGE_SIZE}
            onClick={() => setPage((p) => p + 1)}>
            Siguiente
          </button>
        </div>
      </Card>
    </div>
  );
};
