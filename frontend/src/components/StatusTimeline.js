import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

const STAGE_COLORS = {
  placed: '#3B82F6',
  confirmed: '#8B5CF6',
  preparing: '#F59E0B',
  shipped: '#06B6D4',
  delivered: '#10B981',
};

export default function StatusTimeline() {
  const [orders, setOrders] = useState([]);
  const [stages, setStages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [limit, setLimit] = useState(8);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setLoading(true);
    fetch(`/api/custom-views/status-timeline?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setOrders(data.orders || []);
        setStages(data.stages || []);
        setLoading(false);
      })
      .catch((e) => {
        setErr(e.message);
        setLoading(false);
      });
  }, [limit]);

  if (loading) return <div style={{ padding: 16 }}>Loading status timeline…</div>;
  if (err) return <div style={{ padding: 16, color: '#dc2626' }}>Error: {err}</div>;
  if (!orders.length) return <div style={{ padding: 16, color: '#64748b' }}>No orders to display.</div>;

  return (
    <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Status Timeline (hours per stage)</h3>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748b' }}>
            Horizontal stacked bars show time spent in each status per order.
          </p>
        </div>
        <select
          value={limit}
          onChange={(e) => setLimit(parseInt(e.target.value, 10))}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
        >
          <option value={5}>5 orders</option>
          <option value={8}>8 orders</option>
          <option value={15}>15 orders</option>
          <option value={30}>30 orders</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={Math.max(220, orders.length * 36)}>
        <BarChart data={orders} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 10 }}>
          <XAxis type="number" unit="h" />
          <YAxis dataKey="label" type="category" width={100} />
          <Tooltip formatter={(value) => `${value} h`} />
          <Legend />
          {stages.map((stage) => (
            <Bar
              key={stage}
              dataKey={stage}
              stackId="a"
              fill={STAGE_COLORS[stage] || '#94a3b8'}
              name={stage[0].toUpperCase() + stage.slice(1)}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
