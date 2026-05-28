import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';
import './Login.css';

export const Login = () => {
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.access_token);
        navigate('/precipitation');
      } else {
        setError(data.detail || 'Error al iniciar sesión.');
      }
    } catch {
      setError('No se pudo conectar con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <img src="/logo/Logo.png" alt="Alerto" className="auth-brand-logo" />
        <div className="auth-brand-tagline">
          <strong>Sistema de Monitoreo</strong>
          Monitoreo de precipitación y alertas de riesgo en tiempo real
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-mobile-logo">
            <img src="/logo/Logo.png" alt="Alerto" />
          </div>

          <div className="auth-header">
            <h1>Bienvenido de nuevo</h1>
            <p>Ingresa tus credenciales para continuar</p>
          </div>

          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label className="form-label" htmlFor="email">Correo Electrónico</label>
              <div className="input-wrapper">
                <Mail className="input-icon" size={18} />
                <input
                  id="email"
                  type="email"
                  className="form-input with-icon"
                  placeholder="usuario@alerto.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Contraseña</label>
              <div className="input-wrapper">
                <Lock className="input-icon" size={18} />
                <input
                  id="password"
                  type="password"
                  className="form-input with-icon"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {error && <p className="auth-error">{error}</p>}

            <div className="auth-options">
              <Link to="/reset-password" className="auth-link">
                ¿Olvidaste tu contraseña?
              </Link>
            </div>

            <button type="submit" className="btn-primary auth-submit-btn" disabled={loading}>
              {loading ? 'Ingresando...' : 'Ingresar al Sistema'}
            </button>

            <p className="auth-footer">
              ¿No tienes cuenta?{' '}
              <Link to="/register" className="auth-link">Regístrate</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};
