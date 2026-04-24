import React, { useState } from 'react';
import { api } from '../api';
import { useToast } from '../components/Toast';

export default function ForgotPassword({ onNavigate }) {
  const [step, setStep] = useState('request'); // request, confirm
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { addToast } = useToast();

  async function handleRequest(ev) {
    ev.preventDefault();
    if (!email.trim()) { setErrors({ email: 'Email is required' }); return; }
    setLoading(true);
    try {
      const data = await api.resetPasswordRequest({ email });
      if (data.token) setToken(data.token); // In dev, token is returned
      addToast('Reset link sent! Check your email.', 'info');
      setStep('confirm');
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm(ev) {
    ev.preventDefault();
    const e = {};
    if (!token.trim()) e.token = 'Reset token is required';
    if (newPassword.length < 8) e.newPassword = 'Password must be at least 8 characters';
    if (Object.keys(e).length) { setErrors(e); return; }
    setLoading(true);
    try {
      await api.resetPasswordConfirm({ token, new_password: newPassword });
      addToast('Password reset successfully! Please login.', 'success');
      onNavigate('login');
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Reset Password</h1>
        <p className="subtitle">{step === 'request' ? 'Enter your email to receive a reset link' : 'Enter the reset token and new password'}</p>

        {step === 'request' ? (
          <form onSubmit={handleRequest}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className={`form-input ${errors.email ? 'error' : ''}`} type="email" value={email}
                onChange={e => { setEmail(e.target.value); setErrors({}); }} placeholder="your@email.com" />
              {errors.email && <p className="form-error">{errors.email}</p>}
            </div>
            <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }} disabled={loading}>
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirm}>
            <div className="form-group">
              <label className="form-label">Reset Token</label>
              <input className={`form-input ${errors.token ? 'error' : ''}`} value={token}
                onChange={e => setToken(e.target.value)} placeholder="Paste reset token" />
              {errors.token && <p className="form-error">{errors.token}</p>}
            </div>
            <div className="form-group">
              <label className="form-label">New Password</label>
              <input className={`form-input ${errors.newPassword ? 'error' : ''}`} type="password" value={newPassword}
                onChange={e => setNewPassword(e.target.value)} placeholder="Min 8 chars with upper, lower, digit, special" />
              {errors.newPassword && <p className="form-error">{errors.newPassword}</p>}
            </div>
            <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }} disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <div className="auth-link">
          <a onClick={() => onNavigate('login')}>Back to login</a>
        </div>
      </div>
    </div>
  );
}
