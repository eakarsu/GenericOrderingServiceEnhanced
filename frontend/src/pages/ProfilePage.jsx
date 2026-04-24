import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useToast } from '../components/Toast';

export default function ProfilePage({ user, onUserUpdate }) {
  const [profile, setProfile] = useState({ first_name: '', last_name: '', phone: '' });
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [settings, setSettings] = useState({ theme: 'light', notifications_enabled: true, language: 'en', timezone: 'UTC', items_per_page: 10 });
  const [errors, setErrors] = useState({});
  const { addToast } = useToast();

  useEffect(() => {
    if (user) {
      setProfile({ first_name: user.first_name || '', last_name: user.last_name || '', phone: user.phone || '' });
    }
    api.getSettings().then(setSettings).catch(() => {});
  }, [user]);

  async function handleProfileSave(ev) {
    ev.preventDefault();
    try {
      const data = await api.updateProfile(profile);
      addToast('Profile updated', 'success');
      if (onUserUpdate) onUserUpdate({ ...user, ...profile });
    } catch (err) { addToast(err.message, 'error'); }
  }

  async function handlePasswordChange(ev) {
    ev.preventDefault();
    const e = {};
    if (!passwords.current_password) e.current_password = 'Required';
    if (passwords.new_password.length < 8) e.new_password = 'At least 8 characters';
    else if (!/[A-Z]/.test(passwords.new_password)) e.new_password = 'Needs uppercase';
    else if (!/[a-z]/.test(passwords.new_password)) e.new_password = 'Needs lowercase';
    else if (!/\d/.test(passwords.new_password)) e.new_password = 'Needs a digit';
    else if (!/[!@#$%^&*(),.?":{}|<>]/.test(passwords.new_password)) e.new_password = 'Needs a special character';
    if (passwords.new_password !== passwords.confirm_password) e.confirm_password = 'Passwords do not match';
    if (Object.keys(e).length) { setErrors(e); return; }
    try {
      await api.changePassword({ current_password: passwords.current_password, new_password: passwords.new_password });
      addToast('Password changed', 'success');
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
      setErrors({});
    } catch (err) { addToast(err.message, 'error'); }
  }

  async function handleSettingsSave() {
    try {
      await api.updateSettings(settings);
      addToast('Settings saved', 'success');
    } catch (err) { addToast(err.message, 'error'); }
  }

  return (
    <div className="profile-container">
      <h2 style={{ fontSize: '1.375rem', fontWeight: '700', marginBottom: '1.25rem' }}>Profile & Settings</h2>

      <div className="profile-section">
        <h3>Profile Information</h3>
        <form onSubmit={handleProfileSave}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input className="form-input" value={profile.first_name} onChange={e => setProfile({ ...profile, first_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input className="form-input" value={profile.last_name} onChange={e => setProfile({ ...profile, last_name: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input className="form-input" value={profile.phone} onChange={e => setProfile({ ...profile, phone: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" value={user?.email || ''} disabled style={{ background: '#f8fafc' }} />
            <p className="form-help">Email cannot be changed</p>
          </div>
          <div className="form-group">
            <label className="form-label">Role</label>
            <input className="form-input" value={user?.role || ''} disabled style={{ background: '#f8fafc' }} />
          </div>
          <button className="btn btn-primary" type="submit">Save Profile</button>
        </form>
      </div>

      <div className="profile-section">
        <h3>Change Password</h3>
        <form onSubmit={handlePasswordChange}>
          <div className="form-group">
            <label className="form-label">Current Password</label>
            <input className={`form-input ${errors.current_password ? 'error' : ''}`} type="password" value={passwords.current_password}
              onChange={e => setPasswords({ ...passwords, current_password: e.target.value })} />
            {errors.current_password && <p className="form-error">{errors.current_password}</p>}
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">New Password</label>
              <input className={`form-input ${errors.new_password ? 'error' : ''}`} type="password" value={passwords.new_password}
                onChange={e => setPasswords({ ...passwords, new_password: e.target.value })} />
              {errors.new_password && <p className="form-error">{errors.new_password}</p>}
              <p className="form-help">Min 8 chars, uppercase, lowercase, digit, special char</p>
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <input className={`form-input ${errors.confirm_password ? 'error' : ''}`} type="password" value={passwords.confirm_password}
                onChange={e => setPasswords({ ...passwords, confirm_password: e.target.value })} />
              {errors.confirm_password && <p className="form-error">{errors.confirm_password}</p>}
            </div>
          </div>
          <button className="btn btn-primary" type="submit">Change Password</button>
        </form>
      </div>

      <div className="profile-section">
        <h3>Preferences</h3>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Theme</label>
            <select className="form-input" value={settings.theme} onChange={e => setSettings({ ...settings, theme: e.target.value })}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Language</label>
            <select className="form-input" value={settings.language} onChange={e => setSettings({ ...settings, language: e.target.value })}>
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Timezone</label>
            <select className="form-input" value={settings.timezone} onChange={e => setSettings({ ...settings, timezone: e.target.value })}>
              <option value="UTC">UTC</option>
              <option value="US/Eastern">US Eastern</option>
              <option value="US/Central">US Central</option>
              <option value="US/Pacific">US Pacific</option>
              <option value="Europe/London">London</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Items Per Page</label>
            <select className="form-input" value={settings.items_per_page} onChange={e => setSettings({ ...settings, items_per_page: parseInt(e.target.value) })}>
              <option value="10">10</option>
              <option value="15">15</option>
              <option value="20">20</option>
              <option value="25">25</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
        <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input type="checkbox" checked={settings.notifications_enabled}
            onChange={e => setSettings({ ...settings, notifications_enabled: e.target.checked })} />
          <label className="form-label" style={{ margin: 0 }}>Enable Notifications</label>
        </div>
        <button className="btn btn-primary" onClick={handleSettingsSave}>Save Preferences</button>
      </div>
    </div>
  );
}
