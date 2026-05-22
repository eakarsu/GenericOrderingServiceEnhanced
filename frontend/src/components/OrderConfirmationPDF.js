import React, { useEffect, useState } from 'react';

export default function OrderConfirmationPDF() {
  const [orders, setOrders] = useState([]);
  const [orderId, setOrderId] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/api/orders/?limit=50', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.ok ? r.json() : { orders: [] })
      .then((d) => {
        const list = Array.isArray(d) ? d : (d.orders || d.items || []);
        setOrders(list);
        if (list.length > 0) setOrderId(String(list[0].id));
      })
      .catch(() => {});
  }, []);

  async function download() {
    setErr(null); setMsg(null);
    if (!orderId) { setErr('Please pick or enter an order ID'); return; }
    setBusy(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/custom-views/order-confirmation-pdf?order_id=${orderId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.detail || `HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `confirmation_order_${orderId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setMsg(`Downloaded confirmation_order_${orderId}.pdf`);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div data-testid="order-confirmation-pdf" style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Order Confirmation PDF</h3>
      <p style={{ margin: '4px 0 16px', color: '#64748b', fontSize: 13 }}>
        Generate and download a formal confirmation PDF for any order.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 12, alignItems: 'end', marginBottom: 12 }}>
        <div>
          <label style={{ fontSize: 12, color: '#475569', fontWeight: 600 }}>Pick an order</label>
          <select
            data-testid="cpdf-order-select"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            style={{ width: '100%', padding: '8px 10px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: 13, marginTop: 4 }}
          >
            {orders.length === 0 && <option value="">— no orders found —</option>}
            {orders.map((o) => (
              <option key={o.id} value={o.id}>
                Order #{o.id} — {o.status} — ${(o.total || 0).toFixed(2)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#475569', fontWeight: 600 }}>…or enter Order ID</label>
          <input
            data-testid="cpdf-order-input"
            type="number"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            placeholder="e.g. 12"
            style={{ width: '100%', padding: '8px 10px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: 13, marginTop: 4 }}
          />
        </div>
        <button
          data-testid="cpdf-download"
          onClick={download}
          disabled={busy || !orderId}
          style={{
            padding: '9px 18px',
            background: busy ? '#94a3b8' : '#3B82F6',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            fontWeight: 600,
            cursor: busy ? 'not-allowed' : 'pointer',
            fontSize: 13,
          }}
        >
          {busy ? 'Generating…' : 'Download PDF'}
        </button>
      </div>

      {msg && <div style={{ padding: '8px 12px', background: '#dcfce7', color: '#166534', borderRadius: 6, fontSize: 13 }}>{msg}</div>}
      {err && <div style={{ padding: '8px 12px', background: '#fee2e2', color: '#991b1b', borderRadius: 6, fontSize: 13 }}>Error: {err}</div>}

      <div style={{ marginTop: 16, padding: 12, background: '#f8fafc', borderRadius: 6, fontSize: 12, color: '#64748b' }}>
        The PDF includes a confirmation code, customer info, sector, shipping address, payment method, line items, subtotal, tax and total.
      </div>
    </div>
  );
}
