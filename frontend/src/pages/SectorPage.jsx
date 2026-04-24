import React, { useState, useEffect } from 'react';
import { api, downloadExport } from '../api';
import { useToast } from '../components/Toast';
import { SkeletonTable } from '../components/LoadingSkeleton';
import EmptyState from '../components/EmptyState';
import Pagination from '../components/Pagination';
import ConfirmDialog from '../components/ConfirmDialog';

export default function SectorPage({ sectorId, onNavigate, user }) {
  const [sector, setSector] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [perPage] = useState(10);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterAvailable, setFilterAvailable] = useState('');
  const [selected, setSelected] = useState([]);
  const [detailItem, setDetailItem] = useState(null);
  const [editItem, setEditItem] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);
  const { addToast } = useToast();

  useEffect(() => { loadSector(); }, []);
  useEffect(() => { loadItems(); }, [page, search, sortBy, sortOrder, filterCategory, filterAvailable]);

  async function loadSector() {
    try {
      const s = await api.getSector(sectorId);
      setSector(s);
    } catch (err) {
      addToast('Failed to load sector', 'error');
    }
  }

  async function loadItems() {
    setLoading(true);
    try {
      const params = { page, per_page: perPage, sort_by: sortBy, sort_order: sortOrder, sector_id: sectorId };
      if (search) params.search = search;
      if (filterCategory) params.category_id = filterCategory;
      if (filterAvailable !== '') params.is_available = filterAvailable;
      const data = await api.getItems(params);
      setItems(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      addToast('Failed to load items', 'error');
    } finally {
      setLoading(false);
    }
  }

  function handleSort(col) {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortOrder('asc');
    }
    setPage(1);
  }

  function toggleSelectAll() {
    if (selected.length === items.length) setSelected([]);
    else setSelected(items.map(i => i.id));
  }

  function toggleSelect(id) {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }

  async function handleDelete(id) {
    try {
      await api.deleteItem(id);
      addToast('Item deleted', 'success');
      setConfirmDelete(null);
      setDetailItem(null);
      loadItems();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkDelete() {
    try {
      await api.bulkDeleteItems(selected);
      addToast(`${selected.length} items deleted`, 'success');
      setSelected([]);
      setConfirmBulkDelete(false);
      loadItems();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkUpdate(updates) {
    try {
      await api.bulkUpdateItems(selected, updates);
      addToast(`${selected.length} items updated`, 'success');
      setSelected([]);
      loadItems();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleSaveEdit() {
    try {
      await api.updateItem(editItem.id, {
        name: editItem.name, description: editItem.description,
        price: parseFloat(editItem.price), is_available: editItem.is_available, tags: editItem.tags
      });
      addToast('Item updated', 'success');
      setEditItem(null);
      loadItems();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  const isManager = user?.role === 'admin' || user?.role === 'manager';

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <button className="btn btn-outline btn-sm" onClick={() => onNavigate('dashboard')}>&larr; Back</button>
        <div>
          <h2 style={{ fontSize: '1.375rem', fontWeight: '700' }}>{sector?.name || 'Sector'}</h2>
          {sector && <p style={{ fontSize: '0.85rem', color: '#64748b' }}>{sector.description}</p>}
        </div>
      </div>

      <div className="table-container">
        <div className="table-toolbar">
          <input className="search-input" placeholder="Search items..." value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }} />
          {sector?.categories && (
            <select className="filter-select" value={filterCategory} onChange={e => { setFilterCategory(e.target.value); setPage(1); }}>
              <option value="">All Categories</option>
              {sector.categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          )}
          <select className="filter-select" value={filterAvailable} onChange={e => { setFilterAvailable(e.target.value); setPage(1); }}>
            <option value="">All Status</option>
            <option value="true">Available</option>
            <option value="false">Unavailable</option>
          </select>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {selected.length > 0 && isManager && (
              <>
                <button className="btn btn-danger btn-sm" onClick={() => setConfirmBulkDelete(true)}>
                  Delete ({selected.length})
                </button>
                <button className="btn btn-outline btn-sm" onClick={() => handleBulkUpdate({ is_available: true })}>
                  Enable
                </button>
                <button className="btn btn-outline btn-sm" onClick={() => handleBulkUpdate({ is_available: false })}>
                  Disable
                </button>
              </>
            )}
            <button className="btn btn-outline btn-sm" onClick={() => downloadExport(`/export/items/csv?sector_id=${sectorId}`, `${sector?.slug}_items.csv`)}>
              CSV
            </button>
            <button className="btn btn-outline btn-sm" onClick={() => downloadExport(`/export/items/pdf?sector_id=${sectorId}`, `${sector?.slug}_items.html`)}>
              PDF
            </button>
          </div>
        </div>

        {loading ? <SkeletonTable /> : items.length === 0 ? (
          <EmptyState icon="📋" title="No items found" message="Try adjusting your search or filters." />
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  {isManager && (
                    <th className="checkbox-cell">
                      <input type="checkbox" checked={selected.length === items.length && items.length > 0}
                        onChange={toggleSelectAll} />
                    </th>
                  )}
                  <th onClick={() => handleSort('name')}>Name {sortBy === 'name' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th>Category</th>
                  <th onClick={() => handleSort('price')}>Price {sortBy === 'price' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th>Status</th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id} onClick={() => setDetailItem(item)}>
                    {isManager && (
                      <td className="checkbox-cell" onClick={e => e.stopPropagation()}>
                        <input type="checkbox" checked={selected.includes(item.id)}
                          onChange={() => toggleSelect(item.id)} />
                      </td>
                    )}
                    <td style={{ fontWeight: 500 }}>{item.name}</td>
                    <td>{item.category_name}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td><span className={`badge ${item.is_available ? 'badge-available' : 'badge-unavailable'}`}>
                      {item.is_available ? 'Available' : 'Unavailable'}
                    </span></td>
                    <td style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{item.tags}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination page={page} totalPages={totalPages} total={total} perPage={perPage} onPageChange={setPage} />
          </>
        )}
      </div>

      {/* Detail Modal */}
      {detailItem && !editItem && (
        <div className="modal-overlay" onClick={() => setDetailItem(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{detailItem.name}</h2>
              <button className="modal-close" onClick={() => setDetailItem(null)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-field"><div className="detail-label">ID</div><div className="detail-value">#{detailItem.id}</div></div>
                <div className="detail-field"><div className="detail-label">Price</div><div className="detail-value">${detailItem.price.toFixed(2)}</div></div>
                <div className="detail-field"><div className="detail-label">Category</div><div className="detail-value">{detailItem.category_name || 'N/A'}</div></div>
                <div className="detail-field"><div className="detail-label">Status</div><div className="detail-value"><span className={`badge ${detailItem.is_available ? 'badge-available' : 'badge-unavailable'}`}>{detailItem.is_available ? 'Available' : 'Unavailable'}</span></div></div>
                <div className="detail-field"><div className="detail-label">Tags</div><div className="detail-value">{detailItem.tags || 'None'}</div></div>
                <div className="detail-field"><div className="detail-label">Created</div><div className="detail-value">{new Date(detailItem.created_at).toLocaleDateString()}</div></div>
              </div>
              <div className="detail-field" style={{ marginTop: '1rem' }}>
                <div className="detail-label">Description</div>
                <div className="detail-value">{detailItem.description || 'No description'}</div>
              </div>
            </div>
            {isManager && (
              <div className="modal-footer">
                <button className="btn btn-danger" onClick={() => setConfirmDelete(detailItem.id)}>Delete</button>
                <button className="btn btn-primary" onClick={() => setEditItem({ ...detailItem })}>Edit</button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editItem && (
        <div className="modal-overlay" onClick={() => setEditItem(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Item</h2>
              <button className="modal-close" onClick={() => setEditItem(null)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Name</label>
                <input className="form-input" value={editItem.name} onChange={e => setEditItem({ ...editItem, name: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-input" rows={3} value={editItem.description} onChange={e => setEditItem({ ...editItem, description: e.target.value })} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Price</label>
                  <input className="form-input" type="number" step="0.01" value={editItem.price} onChange={e => setEditItem({ ...editItem, price: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Available</label>
                  <select className="form-input" value={editItem.is_available} onChange={e => setEditItem({ ...editItem, is_available: e.target.value === 'true' })}>
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Tags</label>
                <input className="form-input" value={editItem.tags} onChange={e => setEditItem({ ...editItem, tags: e.target.value })} />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setEditItem(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSaveEdit}>Save Changes</button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog open={!!confirmDelete} title="Delete Item"
        message="Are you sure you want to delete this item? This action cannot be undone."
        onConfirm={() => handleDelete(confirmDelete)} onCancel={() => setConfirmDelete(null)} />

      <ConfirmDialog open={confirmBulkDelete} title="Bulk Delete"
        message={`Are you sure you want to delete ${selected.length} selected items?`}
        onConfirm={handleBulkDelete} onCancel={() => setConfirmBulkDelete(false)} />
    </div>
  );
}
