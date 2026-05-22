import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList,
} from 'recharts';

const STAGE_COLORS = {
  placed: '#3B82F6',
  confirmed: '#8B5CF6',
  preparing: '#F59E0B',
  shipped: '#06B6D4',
  delivered: '#10B981',
};

export default function OrderFlow() {
  const [stages, setStages] = useState([]);
  const [meta, setMeta] = useState({ total_orders: 0, delivered: 0 });
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/api/custom-views/order-flow', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setStages(data.stages || []);
        setMeta({ total_orders: data.total_orders, delivered: data.delivered });
        setLoading(false);
      })
      .catch((e) => {
        setErr(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: 16 }}>Loading order flow…</div>;
  if (err) return <div style={{ padding: 16, color: '#dc2626' }}>Error: {err}</div>;

  const conversion = meta.total_orders
    ? ((meta.delivered / meta.total_orders) * 100).toFixed(1)
    : '0.0';

  return (
    <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <div style={{ marginBottom: 12 }}>
        <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Order Flow Funnel</h3>
        <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748b' }}>
          Vertical funnel: placed → confirmed → preparing → shipped → delivered. Overall conversion: <strong>{conversion}%</strong>
        </p>
      </div>
      <ResponsiveContainer width="100%" height={340}>
        <BarChart
          data={stages}
          layout="vertical"
          margin={{ top: 10, right: 60, left: 30, bottom: 10 }}
        >
          <XAxis type="number" />
          <YAxis dataKey="label" type="category" width={90} />
          <Tooltip
            formatter={(value, name, props) => [
              `${value} orders (${props.payload.conversion_pct}% retained)`,
              'Count',
            ]}
          />
          <Bar dataKey="count" radius={[0, 6, 6, 0]}>
            {stages.map((s) => (
              <Cell key={s.stage} fill={STAGE_COLORS[s.stage] || '#94a3b8'} />
            ))}
            <LabelList dataKey="count" position="right" style={{ fontSize: 12, fontWeight: 600 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ marginTop: 12, display: 'flex', gap: 12, flexWrap: 'wrap', fontSize: 12, color: '#475569' }}>
        {stages.map((s) => (
          <span key={s.stage} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 10, height: 10, background: STAGE_COLORS[s.stage], borderRadius: 2 }} />
            {s.label}: {s.count}{s.drop_off > 0 ? ` (−${s.drop_off})` : ''}
          </span>
        ))}
      </div>
    </div>
  );
}
