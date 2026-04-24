import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SkeletonCards } from '../components/LoadingSkeleton';
import EmptyState from '../components/EmptyState';

const SECTOR_ICONS = {
  utensils: '🍽️', car: '🚗', scissors: '✂️', 'heart-pulse': '❤️', dumbbell: '💪',
  house: '🏠', 'paw-print': '🐾', 'graduation-cap': '🎓', 'calendar-days': '📅',
  landmark: '🏦', 'shield-check': '🛡️', monitor: '💻', scale: '⚖️', truck: '🚚',
  plane: '✈️', camera: '📷', shirt: '👔', box: '📦', building: '🏢'
};

export default function Dashboard({ onNavigate, user }) {
  const [sectors, setSectors] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [sectorsData, statsData] = await Promise.all([
        api.getSectors({ per_page: 50 }),
        api.getStats()
      ]);
      setSectors(sectorsData.items);
      setStats(statsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const filteredSectors = sectors.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.description.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div>
        <div className="stats-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: '100px', borderRadius: '0.625rem' }} />
          ))}
        </div>
        <SkeletonCards count={8} />
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.375rem', fontWeight: '700', marginBottom: '1.25rem' }}>Dashboard</h2>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Total Sectors</h4>
            <div className="stat-value">{stats.total_sectors}</div>
            <div className="stat-sub">Service categories</div>
          </div>
          <div className="stat-card">
            <h4>Total Items</h4>
            <div className="stat-value">{stats.total_items}</div>
            <div className="stat-sub">Products & services</div>
          </div>
          <div className="stat-card">
            <h4>Total Orders</h4>
            <div className="stat-value">{stats.total_orders}</div>
            <div className="stat-sub">{stats.pending_orders} pending</div>
          </div>
          <div className="stat-card">
            <h4>Total Users</h4>
            <div className="stat-value">{stats.total_users}</div>
            <div className="stat-sub">Registered accounts</div>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600' }}>Service Sectors</h3>
        <input className="search-input" placeholder="Search sectors..." value={search}
          onChange={e => setSearch(e.target.value)} />
      </div>

      {filteredSectors.length === 0 ? (
        <EmptyState icon="🔍" title="No sectors found" message="Try a different search term." />
      ) : (
        <div className="cards-grid">
          {filteredSectors.map(sector => (
            <div key={sector.id} className="sector-card" onClick={() => onNavigate('sector', sector.id)}>
              <div className="sector-card-header">
                <div className="sector-icon" style={{ background: sector.color }}>
                  {SECTOR_ICONS[sector.icon] || '📋'}
                </div>
                <div>
                  <h3>{sector.name}</h3>
                  <span className="item-count-badge">{sector.item_count} items</span>
                </div>
              </div>
              <p>{sector.description}</p>
              <div className="sector-card-footer">
                <span>{sector.is_active ? '● Active' : '○ Inactive'}</span>
                <span>Click to view &rarr;</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
