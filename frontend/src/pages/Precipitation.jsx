import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Droplets, Wind, TrendingUp } from 'lucide-react';
import { authFetch } from '../utils/auth';
import './Precipitation.css';

export const Precipitation = () => {
  const [current, setCurrent] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [curRes, histRes] = await Promise.all([
          authFetch('/api/precipitation/current'),
          authFetch('/api/precipitation/history?limit=72'),
        ]);
        if (curRes.ok) setCurrent(await curRes.json());
        if (histRes.ok) {
          const data = await histRes.json();
          setHistory(
            data.map((item) => ({
              time: new Date(item.time_local).toLocaleTimeString([], {
                hour: '2-digit', minute: '2-digit',
              }),
              mm: parseFloat(item.precipitation_mm) || 0,
            })).reverse()
          );
        }
      } catch (err) {
        console.error('Error fetching precipitation:', err);
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
          <h1>Precipitación</h1>
          <p className="text-muted">Datos actuales e histórico de lluvia</p>
        </div>
      </div>

      <div className="metrics-grid">
        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Última hora</h3>
            <div className="metric-icon"><Droplets size={24} /></div>
          </div>
          <div className="metric-value">
            {current ? `${current.precipitation_1h} mm` : '—'}
          </div>
          <p className="metric-trend text-muted">Precipitación 1h</p>
        </Card>

        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Últimas 3 horas</h3>
            <div className="metric-icon"><Droplets size={24} /></div>
          </div>
          <div className="metric-value">
            {current ? `${current.precipitation_3h} mm` : '—'}
          </div>
          <p className="metric-trend text-muted">Precipitación 3h</p>
        </Card>

        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Últimas 6 horas</h3>
            <div className="metric-icon"><Droplets size={24} /></div>
          </div>
          <div className="metric-value">
            {current ? `${current.precipitation_6h} mm` : '—'}
          </div>
          <p className="metric-trend text-muted">Precipitación 6h</p>
        </Card>

        <Card className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Humedad promedio 6h</h3>
            <div className="metric-icon"><Wind size={24} /></div>
          </div>
          <div className="metric-value">
            {current ? `${current.humidity_avg_6h}%` : '—'}
          </div>
          <p className="metric-trend text-muted">
            <TrendingUp size={14} />
            Tendencia: {current ? current.trend_1h : '—'}
          </p>
        </Card>
      </div>

      <Card title="Histórico de Precipitación (últimas 72h)" className="chart-card">
        <div className="chart-container">
          {loading ? (
            <div className="chart-empty">Cargando datos...</div>
          ) : history.length === 0 ? (
            <div className="chart-empty">No hay datos históricos disponibles.</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="time" stroke="#64748b"
                  tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis stroke="#64748b"
                  tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: 'none',
                    boxShadow: 'var(--shadow-md)' }} />
                <Line type="monotone" dataKey="mm" name="mm de lluvia"
                  stroke="var(--primary-color)" strokeWidth={3}
                  dot={false} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>
    </div>
  );
};
