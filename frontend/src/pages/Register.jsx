import React, { useState } from 'react';
import { api } from '../api';
import { useToast } from '../components/Toast';

function getPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
  if (score <= 2) return { level: 'weak', color: '#ef4444', width: '25%' };
  if (score <= 4) return { level: 'fair', color: '#f59e0b', width: '50%' };
  if (score <= 5) return { level: 'good', color: '#3b82f6', width: '75%' };
  return { level: 'strong', color: '#10b981', width: '100%' };
}

export default function Register({ onLogin, onNavigate }) {
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '', first_name: '', last_name: '', phone: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const strength = getPasswordStrength(form.password);

  function validate() {
    const e = {};
    if (!form.username.trim() || form.username.length < 3) e.username = 'Username must be at least 3 characters';
    if (!/^[a-zA-Z0-9_]+$/.test(form.username)) e.username = 'Only letters, numbers, and underscores';
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Valid email is required';
    if (form.password.length < 8) e.password = 'At least 8 characters';
    else if (!/[A-Z]/.test(form.password)) e.password = 'Needs an uppercase letter';
    else if (!/[a-z]/.test(form.password)) e.password = 'Needs a lowercase letter';
    else if (!/\d/.test(form.password)) e.password = 'Needs a digit';
    else if (!/[!@#$%^&*(),.?":{}|<>]/.test(form.password)) e.password = 'Needs a special character';
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match';
    if (!form.first_name.trim()) e.first_name = 'First name is required';
    if (!form.last_name.trim()) e.last_name = 'Last name is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(ev) {
    ev.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const { confirmPassword, ...payload } = form;
      const data = await api.register(payload);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      addToast('Account created! Please verify your email.', 'success');
      onLogin(data.user);
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ maxWidth: '480px' }}>
        <h1>Create Account</h1>
        <p className="subtitle">Join OmniAssist AI platform</p>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">First Name *</label>
              <input className={`form-input ${errors.first_name ? 'error' : ''}`} value={form.first_name}
                onChange={e => setForm({ ...form, first_name: e.target.value })} placeholder="John" />
              {errors.first_name && <p className="form-error">{errors.first_name}</p>}
            </div>
            <div className="form-group">
              <label className="form-label">Last Name *</label>
              <input className={`form-input ${errors.last_name ? 'error' : ''}`} value={form.last_name}
                onChange={e => setForm({ ...form, last_name: e.target.value })} placeholder="Doe" />
              {errors.last_name && <p className="form-error">{errors.last_name}</p>}
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Username *</label>
            <input className={`form-input ${errors.username ? 'error' : ''}`} value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })} placeholder="johndoe" />
            {errors.username && <p className="form-error">{errors.username}</p>}
          </div>
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input className={`form-input ${errors.email ? 'error' : ''}`} type="email" value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })} placeholder="john@example.com" />
            {errors.email && <p className="form-error">{errors.email}</p>}
          </div>
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input className="form-input" value={form.phone}
              onChange={e => setForm({ ...form, phone: e.target.value })} placeholder="+1234567890" />
          </div>
          <div className="form-group">
            <label className="form-label">Password *</label>
            <input className={`form-input ${errors.password ? 'error' : ''}`} type="password" value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })} placeholder="Min 8 chars, upper, lower, digit, special" />
            {form.password && (
              <div className="password-strength">
                <div className="password-strength-bar">
                  <div className="password-strength-fill" style={{ width: strength.width, background: strength.color }} />
                </div>
                <div className="password-strength-label" style={{ color: strength.color }}>Password strength: {strength.level}</div>
              </div>
            )}
            {errors.password && <p className="form-error">{errors.password}</p>}
          </div>
          <div className="form-group">
            <label className="form-label">Confirm Password *</label>
            <input className={`form-input ${errors.confirmPassword ? 'error' : ''}`} type="password" value={form.confirmPassword}
              onChange={e => setForm({ ...form, confirmPassword: e.target.value })} placeholder="Repeat password" />
            {errors.confirmPassword && <p className="form-error">{errors.confirmPassword}</p>}
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }} disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <div className="auth-link">
          Already have an account? <a onClick={() => onNavigate('login')}>Sign in</a>
        </div>
      </div>
    </div>
  );
}
