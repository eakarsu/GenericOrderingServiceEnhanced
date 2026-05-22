import React, { useEffect, useState } from 'react';

const STATUS_OPTIONS = [
  'pending', 'confirmed', 'processing', 'preparing', 'shipped',
  'completed', 'delivered', 'cancelled',
];

export default function BulkStatusUpdate() {
  const [orders, setOrders] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [newStatus, setNewStatus] = useState('confirmed');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);

  function loadOrders() {
    const token = localStorage.getItem('token');
    setLoading(true);
    fetch('/api/orders/?per_page=50', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        const items = data.items || data.orders || data || [];
        setOrders(Array.isArray(items) ? items : []);
        setLoading(false);
      })
      .catch((e) => {
        setErr(e.message);
        setLoading(false);
      });
  }

  useEffect(() => { loadOrders(); }, []);

  function toggle(id) {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelectedIds(next);
  }

  function toggleAll() {
    if (selectedIds.size === orders.length) setSelectedIds(new Set());
    else setSelectedIds(new Set(orders.map((o) => o.id)));
  }

  async function submit() {
    if (selectedIds.size === 0) return;
    setSubmitting(true);
    setResult(null);
    setErr(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/api/custom-views/bulk-status-update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          order_ids: Array.from(selectedIds),
          new_status: newStatus,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setResult(data);
      setSelectedIds(new Set());
      loadOrders();
    } catch (e) {
      setErr(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div style={{ padding: 16 }}>Loading orders…</div>;

  return (
    <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Bulk Status Update</h3>
      <p style={{ margin: '4px 0 12px', fontSize: 13, color: '#64748b' }}>
        Select multiple orders, choose a new status, and apply.
      </p>

      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
        <label style={{ fontSize: 13, color: '#475569' }}>New status:</label>
        <select
          value={newStatus}
          onChange={(e) => setNewStatus(e.target.value)}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
        >
          {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <button
          onClick={submit}
          disabled={selectedIds.size === 0 || submitting}
          style={{
            padding: '6px 14px',
            background: '#10B981',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            cursor: selectedIds.size > 0 && !submitting ? 'pointer' : 'not-allowed',
            opacity: selectedIds.size > 0 && !submitting ? 1 : 0.6,
          }}
        >
          {submitting ? 'Applying…' : `Apply to ${selectedIds.size} selected`}
        </button>
      </div>

      <div style={{ maxHeight: 360, overflow: 'auto', border: '1px solid #e2e8f0', borderRadius: 6 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead style={{ background: '#f8fafc', position: 'sticky', top: 0 }}>
            <tr>
              <th style={{ padding: 8, textAlign: 'left' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.size === orders.length && orders.length > 0}
                  onChange={toggleAll}
                />
              </th>
              <th style={{ padding: 8, textAlign: 'left' }}>Order ID</th>
              <th style={{ padding: 8, textAlign: 'left' }}>Status</th>
              <th style={{ padding: 8, textAlign: 'right' }}>Total</th>
              <th style={{ padding: 8, textAlign: 'left' }}>Created</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 && (
              <tr><td colSpan={5} style={{ padding: 16, textAlign: 'center', color: '#94a3b8' }}>No orders</td></tr>
            )}
            {orders.map((o) => (
              <tr key={o.id} style={{ borderTop: '1px solid #e2e8f0' }}>
                <td style={{ padding: 8 }}>
                  <input
                    type="checkbox"
                    checked={selectedIds.has(o.id)}
                    onChange={() => toggle(o.id)}
                  />
                </td>
                <td style={{ padding: 8 }}>#{o.id}</td>
                <td style={{ padding: 8 }}>
                  <span style={{
                    padding: '2px 8px', borderRadius: 4, background: '#e0e7ff',
                    color: '#3730a3', fontSize: 11, fontWeight: 600,
                  }}>{o.status}</span>
                </td>
                <td style={{ padding: 8, textAlign: 'right' }}>${(o.total || 0).toFixed(2)}</td>
                <td style={{ padding: 8, color: '#64748b' }}>
                  {o.created_at ? new Date(o.created_at).toLocaleDateString() : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {err && (
        <div style={{ marginTop: 12, padding: '8px 12px', background: '#fee2e2', color: '#991b1b', borderRadius: 6, fontSize: 13 }}>
          Error: {err}
        </div>
      )}
      {result && (
        <div style={{ marginTop: 12, padding: '8px 12px', background: '#dcfce7', color: '#166534', borderRadius: 6, fontSize: 13 }}>
          Updated <strong>{result.updated}</strong> orders to <strong>{result.new_status}</strong>.
          {result.errors && result.errors.length > 0 && (
            <span> {result.errors.length} error(s): {JSON.stringify(result.errors.slice(0, 3))}</span>
          )}
        </div>
      )}
    </div>
  );
}
