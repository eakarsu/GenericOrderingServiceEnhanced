import React, { useState } from 'react';
import { api } from '../api';
import { useToast } from '../components/Toast';

export default function Login({ onLogin, onNavigate }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  function validate() {
    const e = {};
    if (!form.username.trim()) e.username = 'Username is required';
    if (!form.password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(ev) {
    ev.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const data = await api.login(form);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      addToast(`Welcome back, ${data.user.first_name || data.user.username}!`, 'success');
      onLogin(data.user);
    } catch (err) {
      addToast(err.message, 'error');
      setErrors({ general: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>OmniAssist AI</h1>
        <p className="subtitle">Sign in to your account</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input className={`form-input ${errors.username ? 'error' : ''}`} type="text" placeholder="Enter username"
              value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
            {errors.username && <p className="form-error">{errors.username}</p>}
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className={`form-input ${errors.password ? 'error' : ''}`} type="password" placeholder="Enter password"
              value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
            {errors.password && <p className="form-error">{errors.password}</p>}
          </div>
          {errors.general && <p className="form-error" style={{ marginBottom: '1rem' }}>{errors.general}</p>}
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <div className="auth-link">
          <a onClick={() => onNavigate('forgot-password')}>Forgot password?</a>
        </div>
        <div className="auth-link">
          Don't have an account? <a onClick={() => onNavigate('register')}>Sign up</a>
        </div>
      </div>
    </div>
  );
}
