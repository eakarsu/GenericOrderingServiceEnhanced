import React, { useState, useEffect } from 'react';
import { ToastProvider, useToast } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import SectorPage from './pages/SectorPage';
import OrdersPage from './pages/OrdersPage';
import UsersPage from './pages/UsersPage';
import AllItemsPage from './pages/AllItemsPage';
import ProfilePage from './pages/ProfilePage';
import CustomViewsPage from './pages/CustomViewsPage';
import { api } from './api';

function AppContent() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [pageArg, setPageArg] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    const saved = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (saved && token) {
      setUser(JSON.parse(saved));
    } else {
      setCurrentPage('login');
    }
    // Route /custom-views (hash or path) to custom-views page
    function applyRoute() {
      const path = window.location.pathname || '';
      const hash = window.location.hash || '';
      if (path.includes('/custom-views') || hash.includes('custom-views')) {
        setCurrentPage('custom-views');
      }
    }
    applyRoute();
    window.addEventListener('hashchange', applyRoute);
    return () => window.removeEventListener('hashchange', applyRoute);
  }, []);

  function navigate(page, arg) {
    setCurrentPage(page);
    setPageArg(arg || null);
    setSidebarOpen(false);
    window.scrollTo(0, 0);
  }

  function handleLogin(userData) {
    setUser(userData);
    navigate('dashboard');
  }

  async function handleLogout() {
    try { await api.logout(); } catch {}
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('login');
    addToast('Logged out successfully', 'info');
  }

  function handleUserUpdate(updatedUser) {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  }

  // Auth pages (no sidebar)
  if (!user || currentPage === 'login' || currentPage === 'register' || currentPage === 'forgot-password') {
    if (currentPage === 'register') return <Register onLogin={handleLogin} onNavigate={navigate} />;
    if (currentPage === 'forgot-password') return <ForgotPassword onNavigate={navigate} />;
    return <Login onLogin={handleLogin} onNavigate={navigate} />;
  }

  const isManager = user.role === 'admin' || user.role === 'manager';

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h1>OmniAssist AI</h1>
          <p>Universal Service Platform</p>
        </div>
        <nav className="sidebar-nav">
          <div className="sidebar-section">Main</div>
          <a className={currentPage === 'dashboard' ? 'active' : ''} onClick={() => navigate('dashboard')}>
            <span>📊</span> Dashboard
          </a>
          <a className={currentPage === 'all-items' ? 'active' : ''} onClick={() => navigate('all-items')}>
            <span>📋</span> All Items
          </a>
          <a className={currentPage === 'orders' ? 'active' : ''} onClick={() => navigate('orders')}>
            <span>📦</span> Orders
          </a>
          <a className={currentPage === 'custom-views' ? 'active' : ''} onClick={() => navigate('custom-views')} data-testid="nav-custom-views">
            <span>📈</span> Order Views
          </a>

          {isManager && (
            <>
              <div className="sidebar-section">Admin</div>
              <a className={currentPage === 'users' ? 'active' : ''} onClick={() => navigate('users')}>
                <span>👥</span> Users
              </a>
            </>
          )}

          <div className="sidebar-section">Account</div>
          <a className={currentPage === 'profile' ? 'active' : ''} onClick={() => navigate('profile')}>
            <span>⚙️</span> Profile & Settings
          </a>
          <button onClick={handleLogout}>
            <span>🚪</span> Logout
          </button>
        </nav>
      </aside>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 35 }} onClick={() => setSidebarOpen(false)} />}

      {/* Main Content */}
      <div className="main-content">
        <div className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button className="hamburger" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
            <span style={{ fontSize: '0.9rem', color: '#475569' }}>
              {currentPage === 'dashboard' && 'Dashboard'}
              {currentPage === 'sector' && 'Sector Details'}
              {currentPage === 'orders' && 'Orders'}
              {currentPage === 'users' && 'User Management'}
              {currentPage === 'all-items' && 'All Items'}
              {currentPage === 'profile' && 'Profile & Settings'}
              {currentPage === 'custom-views' && 'Order Views'}
            </span>
          </div>
          <div className="topbar-right">
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              {user.first_name || user.username}
            </span>
            <span className={`badge badge-${user.role}`}>{user.role}</span>
          </div>
        </div>

        <div className="page-content">
          <ErrorBoundary>
            {currentPage === 'dashboard' && <Dashboard onNavigate={navigate} user={user} />}
            {currentPage === 'sector' && <SectorPage sectorId={pageArg} onNavigate={navigate} user={user} />}
            {currentPage === 'orders' && <OrdersPage user={user} />}
            {currentPage === 'users' && isManager && <UsersPage user={user} />}
            {currentPage === 'all-items' && <AllItemsPage user={user} onNavigate={navigate} />}
            {currentPage === 'profile' && <ProfilePage user={user} onUserUpdate={handleUserUpdate} />}
            {currentPage === 'custom-views' && <CustomViewsPage user={user} />}
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <ErrorBoundary>
        <AppContent />
      </ErrorBoundary>
    </ToastProvider>
  );
}
