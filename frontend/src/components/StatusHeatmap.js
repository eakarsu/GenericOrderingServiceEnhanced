import React, { useEffect, useState } from 'react';

function cellColor(value, max) {
  if (!max) return '#f1f5f9';
  const ratio = value / max;
  // Blue scale 0..1 from #eff6ff to #1d4ed8
  const start = [239, 246, 255];
  const end = [29, 78, 216];
  const c = start.map((s, i) => Math.round(s + (end[i] - s) * ratio));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

function cellTextColor(value, max) {
  if (!max) return '#94a3b8';
  return value / max > 0.55 ? '#fff' : '#1e293b';
}

export default function StatusHeatmap() {
  const [data, setData] = useState(null);
  const [days, setDays] = useState(14);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setLoading(true);
    fetch(`/api/custom-views/status-heatmap?days=${days}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setErr(e.message); setLoading(false); });
  }, [days]);

  if (loading) return <div style={{ padding: 16 }}>Loading status heatmap…</div>;
  if (err) return <div style={{ padding: 16, color: '#dc2626' }}>Error: {err}</div>;
  if (!data) return null;

  const { buckets, matrix, max_count, total } = data;

  return (
    <div data-testid="status-heatmap" style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Status × Time-of-Day Heatmap</h3>
          <p style={{ margin: '2px 0 0', color: '#64748b', fontSize: 12 }}>
            {total} orders over the last {data.days} days; cells = order counts.
          </p>
        </div>
        <select
          data-testid="hm-days"
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

      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: 4, width: '100%' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '6px 8px', fontSize: 12, color: '#64748b', minWidth: 110 }}>Status</th>
              {buckets.map((b) => (
                <th key={b} style={{ padding: '6px 8px', fontSize: 12, color: '#64748b', textAlign: 'center' }}>{b}</th>
              ))}
              <th style={{ padding: '6px 8px', fontSize: 12, color: '#64748b', textAlign: 'right' }}>Total</th>
            </tr>
          </thead>
          <tbody>
            {matrix.map((row) => {
              const rowTotal = row.counts.reduce((a, b) => a + b, 0);
              return (
                <tr key={row.status}>
                  <td style={{ padding: '6px 8px', fontSize: 13, fontWeight: 600, textTransform: 'capitalize', color: '#0f172a' }}>{row.status}</td>
                  {row.counts.map((v, i) => (
                    <td
                      key={i}
                      data-testid={`hm-cell-${row.status}-${buckets[i]}`}
                      style={{
                        padding: '14px 8px',
                        textAlign: 'center',
                        background: cellColor(v, max_count),
                        color: cellTextColor(v, max_count),
                        borderRadius: 6,
                        fontWeight: 600,
                        fontSize: 13,
                        minWidth: 60,
                      }}
                    >
                      {v}
                    </td>
                  ))}
                  <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{rowTotal}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 14, fontSize: 12, color: '#64748b' }}>
        <span>Less</span>
        <div style={{ display: 'flex', gap: 2 }}>
          {[0, 0.2, 0.4, 0.6, 0.8, 1].map((r, i) => (
            <div key={i} style={{ width: 20, height: 12, background: cellColor(r * max_count, max_count), borderRadius: 2 }} />
          ))}
        </div>
        <span>More</span>
        <span style={{ marginLeft: 12 }}>Max: <b>{max_count}</b></span>
      </div>
    </div>
  );
}
