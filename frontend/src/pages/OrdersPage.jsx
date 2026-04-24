import React, { useState, useEffect } from 'react';
import { api, downloadExport } from '../api';
import { useToast } from '../components/Toast';
import { SkeletonTable } from '../components/LoadingSkeleton';
import EmptyState from '../components/EmptyState';
import Pagination from '../components/Pagination';
import ConfirmDialog from '../components/ConfirmDialog';

export default function OrdersPage({ user }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [perPage] = useState(10);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterStatus, setFilterStatus] = useState('');
  const [selected, setSelected] = useState([]);
  const [detailOrder, setDetailOrder] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);
  const { addToast } = useToast();

  const isManager = user?.role === 'admin' || user?.role === 'manager';

  useEffect(() => { loadOrders(); }, [page, search, sortBy, sortOrder, filterStatus]);

  async function loadOrders() {
    setLoading(true);
    try {
      const params = { page, per_page: perPage, sort_by: sortBy, sort_order: sortOrder };
      if (search) params.search = search;
      if (filterStatus) params.status = filterStatus;
      const data = await api.getOrders(params);
      setOrders(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      addToast('Failed to load orders', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function loadOrderDetail(id) {
    try {
      const data = await api.getOrder(id);
      setDetailOrder(data);
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  function handleSort(col) {
    if (sortBy === col) setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    else { setSortBy(col); setSortOrder('asc'); }
    setPage(1);
  }

  function toggleSelectAll() {
    if (selected.length === orders.length) setSelected([]);
    else setSelected(orders.map(o => o.id));
  }

  function toggleSelect(id) {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }

  async function handleDelete(id) {
    try {
      await api.deleteOrder(id);
      addToast('Order deleted', 'success');
      setConfirmDelete(null);
      setDetailOrder(null);
      loadOrders();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleStatusUpdate(id, status) {
    try {
      await api.updateOrder(id, { status });
      addToast(`Order marked as ${status}`, 'success');
      setDetailOrder(null);
      loadOrders();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkDelete() {
    try {
      await api.bulkDeleteOrders(selected);
      addToast(`${selected.length} orders deleted`, 'success');
      setSelected([]);
      setConfirmBulkDelete(false);
      loadOrders();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkStatusUpdate(status) {
    try {
      await api.bulkUpdateOrders(selected, { status });
      addToast(`${selected.length} orders updated to ${status}`, 'success');
      setSelected([]);
      loadOrders();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.375rem', fontWeight: '700', marginBottom: '1.25rem' }}>Orders</h2>

      <div className="table-container">
        <div className="table-toolbar">
          <input className="search-input" placeholder="Search orders..." value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }} />
          <select className="filter-select" value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setPage(1); }}>
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {selected.length > 0 && isManager && (
              <>
                <button className="btn btn-danger btn-sm" onClick={() => setConfirmBulkDelete(true)}>Delete ({selected.length})</button>
                <select className="filter-select" style={{ fontSize: '0.75rem' }} onChange={e => { if (e.target.value) handleBulkStatusUpdate(e.target.value); e.target.value = ''; }}>
                  <option value="">Bulk Status...</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </>
            )}
            <button className="btn btn-outline btn-sm" onClick={() => downloadExport('/export/orders/csv', 'orders.csv')}>CSV</button>
            <button className="btn btn-outline btn-sm" onClick={() => downloadExport('/export/orders/pdf', 'orders.html')}>PDF</button>
          </div>
        </div>

        {loading ? <SkeletonTable /> : orders.length === 0 ? (
          <EmptyState icon="📦" title="No orders found" message="Orders will appear here once created." />
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  {isManager && <th className="checkbox-cell"><input type="checkbox" checked={selected.length === orders.length && orders.length > 0} onChange={toggleSelectAll} /></th>}
                  <th onClick={() => handleSort('id')}>ID {sortBy === 'id' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th>Customer</th>
                  <th>Sector</th>
                  <th onClick={() => handleSort('status')}>Status {sortBy === 'status' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th onClick={() => handleSort('total')}>Total {sortBy === 'total' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th onClick={() => handleSort('created_at')}>Date {sortBy === 'created_at' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id} onClick={() => loadOrderDetail(order.id)}>
                    {isManager && <td className="checkbox-cell" onClick={e => e.stopPropagation()}><input type="checkbox" checked={selected.includes(order.id)} onChange={() => toggleSelect(order.id)} /></td>}
                    <td>#{order.id}</td>
                    <td>{order.user_name}</td>
                    <td>{order.sector_name}</td>
                    <td><span className={`badge badge-${order.status}`}>{order.status}</span></td>
                    <td>${order.total.toFixed(2)}</td>
                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination page={page} totalPages={totalPages} total={total} perPage={perPage} onPageChange={setPage} />
          </>
        )}
      </div>

      {/* Order Detail Modal */}
      {detailOrder && (
        <div className="modal-overlay" onClick={() => setDetailOrder(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Order #{detailOrder.id}</h2>
              <button className="modal-close" onClick={() => setDetailOrder(null)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-field"><div className="detail-label">Customer</div><div className="detail-value">{detailOrder.user_name}</div></div>
                <div className="detail-field"><div className="detail-label">Sector</div><div className="detail-value">{detailOrder.sector_name}</div></div>
                <div className="detail-field"><div className="detail-label">Status</div><div className="detail-value"><span className={`badge badge-${detailOrder.status}`}>{detailOrder.status}</span></div></div>
                <div className="detail-field"><div className="detail-label">Total</div><div className="detail-value" style={{ fontSize: '1.125rem', fontWeight: '700' }}>${detailOrder.total.toFixed(2)}</div></div>
                <div className="detail-field"><div className="detail-label">Payment</div><div className="detail-value">{detailOrder.payment_method}</div></div>
                <div className="detail-field"><div className="detail-label">Date</div><div className="detail-value">{new Date(detailOrder.created_at).toLocaleString()}</div></div>
              </div>
              {detailOrder.shipping_address && (
                <div className="detail-field" style={{ marginTop: '1rem' }}><div className="detail-label">Address</div><div className="detail-value">{detailOrder.shipping_address}</div></div>
              )}
              {detailOrder.notes && (
                <div className="detail-field" style={{ marginTop: '0.5rem' }}><div className="detail-label">Notes</div><div className="detail-value">{detailOrder.notes}</div></div>
              )}
              {detailOrder.items && detailOrder.items.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div className="detail-label" style={{ marginBottom: '0.5rem' }}>Order Items</div>
                  <table style={{ fontSize: '0.85rem' }}>
                    <thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr></thead>
                    <tbody>
                      {detailOrder.items.map(oi => (
                        <tr key={oi.id} style={{ cursor: 'default' }}>
                          <td>{oi.item_name}</td><td>{oi.quantity}</td><td>${oi.unit_price.toFixed(2)}</td><td>${oi.subtotal.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              {isManager && (
                <>
                  <button className="btn btn-danger" onClick={() => setConfirmDelete(detailOrder.id)}>Delete</button>
                  {detailOrder.status === 'pending' && <button className="btn btn-primary" onClick={() => handleStatusUpdate(detailOrder.id, 'confirmed')}>Confirm</button>}
                  {detailOrder.status === 'confirmed' && <button className="btn btn-primary" onClick={() => handleStatusUpdate(detailOrder.id, 'processing')}>Process</button>}
                  {detailOrder.status === 'processing' && <button className="btn btn-success" onClick={() => handleStatusUpdate(detailOrder.id, 'completed')}>Complete</button>}
                  {detailOrder.status !== 'cancelled' && detailOrder.status !== 'completed' && (
                    <button className="btn btn-outline" onClick={() => handleStatusUpdate(detailOrder.id, 'cancelled')}>Cancel</button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog open={!!confirmDelete} title="Delete Order"
        message="Are you sure you want to delete this order?"
        onConfirm={() => handleDelete(confirmDelete)} onCancel={() => setConfirmDelete(null)} />
      <ConfirmDialog open={confirmBulkDelete} title="Bulk Delete"
        message={`Delete ${selected.length} selected orders?`}
        onConfirm={handleBulkDelete} onCancel={() => setConfirmBulkDelete(false)} />
    </div>
  );
}
