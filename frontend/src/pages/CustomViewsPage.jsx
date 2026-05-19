import React, { useState } from 'react';
import OrderVolumeTimeline from '../components/OrderVolumeTimeline.js';
import StatusHeatmap from '../components/StatusHeatmap.js';
import OrderConfirmationPDF from '../components/OrderConfirmationPDF.js';
import OrderingRulesEditor from '../components/OrderingRulesEditor.js';

const TABS = [
  { id: 'volume', label: 'Order Volume Timeline', icon: '📈' },
  { id: 'heatmap', label: 'Status Heatmap', icon: '🔥' },
  { id: 'confirm', label: 'Confirmation PDF', icon: '🧾' },
  { id: 'rules', label: 'Ordering Rules', icon: '⚙️' },
];

export default function CustomViewsPage({ user }) {
  const [tab, setTab] = useState('volume');

  return (
    <div data-testid="custom-views-page" style={{ padding: 0 }}>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Order Views</h2>
        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>
          Custom visualizations and management tools for the ordering service.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '1px solid #e2e8f0', flexWrap: 'wrap' }}>
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            data-testid={`tab-${t.id}`}
            style={{
              padding: '10px 16px',
              background: tab === t.id ? '#fff' : 'transparent',
              border: 'none',
              borderBottom: tab === t.id ? '2px solid #3B82F6' : '2px solid transparent',
              color: tab === t.id ? '#3B82F6' : '#64748b',
              fontWeight: tab === t.id ? 600 : 500,
              cursor: 'pointer',
              fontSize: 14,
            }}
          >
            <span style={{ marginRight: 6 }}>{t.icon}</span>{t.label}
          </button>
        ))}
      </div>

      <div>
        {tab === 'volume' && <OrderVolumeTimeline />}
        {tab === 'heatmap' && <StatusHeatmap />}
        {tab === 'confirm' && <OrderConfirmationPDF />}
        {tab === 'rules' && <OrderingRulesEditor user={user} />}
      </div>
    </div>
  );
}
