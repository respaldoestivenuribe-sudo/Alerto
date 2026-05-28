import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { AlertTriangle, TrendingUp, Droplets } from 'lucide-react';
import { authFetch } from '../utils/auth';
import './Risk.css';

const BADGE = {
  ROJO:     'badge-danger',
  NARANJA:  'badge-naranja',
  AMARILLO: 'badge-warning',
  VERDE:    'badge-success',
};

export const Risk = () => {
  const [current, setCurrent] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [curRes, histRes] = await Promise.all([
          authFetch('/api/risk/current'),
          authFetch('/api/risk/history?limit=50'),
        ]);
        if (curRes.ok)  setCurrent(await curRes.json());
        if (histRes.ok) setHistory(await histRes.json());
      } catch (err) {
        console.error('Error fetching risk:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60_000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>Riesgo</h1>
          <p className="text-muted">Nivel de riesgo actual e histórico</p>
        </div>
      </div>

      <div className="metrics-grid">
        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Nivel de Riesgo</h3>
            <div className="metric-icon"><AlertTriangle size={24} /></div>
          </div>
          <div className="metric-value">
            {current
              ? <span className={`badge badge-lg ${BADGE[current.nivel_riesgo] ?? ''}`}>
                  {current.nivel_riesgo}
                </span>
              : '—'}
          </div>
          <p className="metric-trend text-muted">
            <TrendingUp size={16} />
            Score: {current ? parseFloat(current.riesgo_score).toFixed(0) : '—'}%
          </p>
        </Card>

        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Nivel de Lluvia</h3>
            <div className="metric-icon"><Droplets size={24} /></div>
          </div>
          <div className="metric-value">
            {current ? parseFloat(current.nivel_lluvia).toFixed(2) : '—'}
          </div>
          <p className="metric-trend text-muted">
            Última evaluación:{' '}
            {current ? new Date(current.evaluated_at).toLocaleString('es-ES') : '—'}
          </p>
        </Card>
      </div>

      <Card title="Histórico de Riesgo (últimos 50 registros)">
        <div className="table-responsive">
          <table className="risk-table" aria-label="Histórico de riesgo">
            <thead>
              <tr>
                <th scope="col">Fecha y hora</th>
                <th scope="col">Nivel</th>
                <th scope="col">Score</th>
                <th scope="col">Precip. 1h</th>
                <th scope="col">Humedad 6h</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="5" className="text-center">Cargando...</td></tr>
              ) : history.length === 0 ? (
                <tr><td colSpan="5" className="text-center">No hay datos disponibles.</td></tr>
              ) : (
                history.map((item, i) => (
                  <tr key={i}>
                    <td>{new Date(item.evaluated_at).toLocaleString('es-ES')}</td>
                    <td>
                      <span className={`badge ${BADGE[item.nivel_riesgo] ?? ''}`}>
                        {item.nivel_riesgo}
                      </span>
                    </td>
                    <td>{parseFloat(item.riesgo_score).toFixed(0)}%</td>
                    <td>{parseFloat(item.precip_1h ?? 0).toFixed(1)} mm</td>
                    <td>{parseFloat(item.humedad_prom_6h ?? 0).toFixed(0)}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
