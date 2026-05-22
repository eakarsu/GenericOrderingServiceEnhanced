import React, { useEffect, useState } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

export default function OrderVolumeTimeline() {
  const [data, setData] = useState(null);
  const [days, setDays] = useState(14);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setLoading(true);
    fetch(`/api/custom-views/order-volume-timeline?days=${days}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setErr(e.message); setLoading(false); });
  }, [days]);

  if (loading) return <div style={{ padding: 16 }}>Loading order volume…</div>;
  if (err) return <div style={{ padding: 16, color: '#dc2626' }}>Error: {err}</div>;
  if (!data) return null;

  return (
    <div data-testid="order-volume-timeline" style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Order Volume Timeline</h3>
          <p style={{ margin: '2px 0 0', color: '#64748b', fontSize: 12 }}>
            Daily orders &amp; revenue over the last {data.days} days.
          </p>
        </div>
        <select
          data-testid="ovt-days"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          style={{ padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: 13 }}
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={60}>Last 60 days</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
        <Stat label="Total Orders" value={data.total_orders} color="#3B82F6" />
        <Stat label="Total Revenue" value={`$${data.total_revenue.toFixed(2)}`} color="#10B981" />
        <Stat label="Avg / Day" value={data.avg_orders_per_day} color="#8B5CF6" />
        <Stat
          label="Peak Day"
          value={data.peak_day ? `${data.peak_day.date.slice(5)} (${data.peak_day.count})` : '—'}
          color="#F59E0B"
        />
      </div>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <AreaChart data={data.series} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="vCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.55} />
                <stop offset="100%" stopColor="#3B82F6" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="vRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity={0.45} />
                <stop offset="100%" stopColor="#10B981" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} tick={{ fontSize: 11 }} />
            <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Area yAxisId="left" type="monotone" dataKey="count" name="Orders" stroke="#3B82F6" fill="url(#vCount)" strokeWidth={2} />
            <Area yAxisId="right" type="monotone" dataKey="revenue" name="Revenue ($)" stroke="#10B981" fill="url(#vRev)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, borderLeft: `3px solid ${color}` }}>
      <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.4 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>{value}</div>
    </div>
  );
}
