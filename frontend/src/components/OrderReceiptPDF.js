import React, { useEffect, useState } from 'react';

export default function OrderReceiptPDF() {
  const [orders, setOrders] = useState([]);
  const [selected, setSelected] = useState('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/api/orders/?per_page=50', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        const items = data.items || data.orders || data || [];
        setOrders(Array.isArray(items) ? items : []);
        if (items.length) setSelected(String(items[0].id));
        setLoading(false);
      })
      .catch((e) => {
        setMsg({ type: 'error', text: e.message });
        setLoading(false);
      });
  }, []);

  async function downloadPDF() {
    if (!selected) return;
    setDownloading(true);
    setMsg(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/api/custom-views/order-receipt?order_id=${selected}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text.slice(0, 120)}`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `receipt_order_${selected}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setMsg({ type: 'success', text: `Receipt for order #${selected} downloaded.` });
    } catch (e) {
      setMsg({ type: 'error', text: e.message });
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Order Receipt PDF</h3>
      <p style={{ margin: '4px 0 12px', fontSize: 13, color: '#64748b' }}>
        Pick an order and download a PDF receipt with line items, tax, total, and tracking.
      </p>
      {loading ? (
        <div>Loading orders…</div>
      ) : (
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontSize: 13, color: '#475569' }}>Order:</label>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #cbd5e1', minWidth: 240 }}
          >
            {orders.length === 0 && <option value="">No orders available</option>}
            {orders.map((o) => (
              <option key={o.id} value={o.id}>
                #{o.id} — {o.status} — ${(o.total || 0).toFixed(2)}
              </option>
            ))}
          </select>
          <button
            onClick={downloadPDF}
            disabled={!selected || downloading}
            style={{
              padding: '8px 16px',
              background: '#3B82F6',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              cursor: selected && !downloading ? 'pointer' : 'not-allowed',
              opacity: selected && !downloading ? 1 : 0.6,
            }}
          >
            {downloading ? 'Generating…' : 'Download PDF Receipt'}
          </button>
        </div>
      )}
      {msg && (
        <div
          style={{
            marginTop: 12,
            padding: '8px 12px',
            borderRadius: 6,
            background: msg.type === 'error' ? '#fee2e2' : '#dcfce7',
            color: msg.type === 'error' ? '#991b1b' : '#166534',
            fontSize: 13,
          }}
        >
          {msg.text}
        </div>
      )}
    </div>
  );
}
