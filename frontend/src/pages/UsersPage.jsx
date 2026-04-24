import React, { useState, useEffect } from 'react';
import { api, downloadExport } from '../api';
import { useToast } from '../components/Toast';
import { SkeletonTable } from '../components/LoadingSkeleton';
import EmptyState from '../components/EmptyState';
import Pagination from '../components/Pagination';
import ConfirmDialog from '../components/ConfirmDialog';

export default function UsersPage({ user }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [perPage] = useState(10);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterRole, setFilterRole] = useState('');
  const [filterActive, setFilterActive] = useState('');
  const [selected, setSelected] = useState([]);
  const [detailUser, setDetailUser] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);
  const { addToast } = useToast();

  const isAdmin = user?.role === 'admin';

  useEffect(() => { loadUsers(); }, [page, search, sortBy, sortOrder, filterRole, filterActive]);

  async function loadUsers() {
    setLoading(true);
    try {
      const params = { page, per_page: perPage, sort_by: sortBy, sort_order: sortOrder };
      if (search) params.search = search;
      if (filterRole) params.role = filterRole;
      if (filterActive !== '') params.is_active = filterActive;
      const data = await api.getUsers(params);
      setUsers(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      addToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  }

  function handleSort(col) {
    if (sortBy === col) setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    else { setSortBy(col); setSortOrder('asc'); }
    setPage(1);
  }

  function toggleSelectAll() {
    if (selected.length === users.length) setSelected([]);
    else setSelected(users.map(u => u.id));
  }

  function toggleSelect(id) {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }

  async function handleDelete(id) {
    try {
      await api.deleteUser(id);
      addToast('User deleted', 'success');
      setConfirmDelete(null);
      setDetailUser(null);
      loadUsers();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkDelete() {
    try {
      await api.bulkDeleteUsers(selected);
      addToast(`${selected.length} users deleted`, 'success');
      setSelected([]);
      setConfirmBulkDelete(false);
      loadUsers();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleRoleUpdate(userId, role) {
    try {
      await api.updateUserRole(userId, { role });
      addToast(`Role updated to ${role}`, 'success');
      setDetailUser(null);
      loadUsers();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  async function handleBulkRoleUpdate(role) {
    try {
      await api.bulkUpdateUsers(selected, { role });
      addToast(`${selected.length} users updated to ${role}`, 'success');
      setSelected([]);
      loadUsers();
    } catch (err) {
      addToast(err.message, 'error');
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.375rem', fontWeight: '700', marginBottom: '1.25rem' }}>Users</h2>

      <div className="table-container">
        <div className="table-toolbar">
          <input className="search-input" placeholder="Search users..." value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }} />
          <select className="filter-select" value={filterRole} onChange={e => { setFilterRole(e.target.value); setPage(1); }}>
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="user">User</option>
            <option value="viewer">Viewer</option>
          </select>
          <select className="filter-select" value={filterActive} onChange={e => { setFilterActive(e.target.value); setPage(1); }}>
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {selected.length > 0 && isAdmin && (
              <>
                <button className="btn btn-danger btn-sm" onClick={() => setConfirmBulkDelete(true)}>Delete ({selected.length})</button>
                <select className="filter-select" style={{ fontSize: '0.75rem' }} onChange={e => { if (e.target.value) handleBulkRoleUpdate(e.target.value); e.target.value = ''; }}>
                  <option value="">Set Role...</option>
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="user">User</option>
                  <option value="viewer">Viewer</option>
                </select>
              </>
            )}
            <button className="btn btn-outline btn-sm" onClick={() => downloadExport('/export/users/csv', 'users.csv')}>CSV</button>
          </div>
        </div>

        {loading ? <SkeletonTable /> : users.length === 0 ? (
          <EmptyState icon="👥" title="No users found" message="Adjust your search or filters." />
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  {isAdmin && <th className="checkbox-cell"><input type="checkbox" checked={selected.length === users.length && users.length > 0} onChange={toggleSelectAll} /></th>}
                  <th onClick={() => handleSort('username')}>Username {sortBy === 'username' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th onClick={() => handleSort('email')}>Email {sortBy === 'email' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th onClick={() => handleSort('created_at')}>Joined {sortBy === 'created_at' && <span className="sort-indicator">{sortOrder === 'asc' ? '▲' : '▼'}</span>}</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} onClick={() => setDetailUser(u)}>
                    {isAdmin && <td className="checkbox-cell" onClick={e => e.stopPropagation()}><input type="checkbox" checked={selected.includes(u.id)} onChange={() => toggleSelect(u.id)} /></td>}
                    <td style={{ fontWeight: 500 }}>{u.username}</td>
                    <td>{u.email}</td>
                    <td>{u.first_name} {u.last_name}</td>
                    <td><span className={`badge badge-${u.role}`}>{u.role}</span></td>
                    <td><span className={`badge ${u.is_active ? 'badge-active' : 'badge-inactive'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination page={page} totalPages={totalPages} total={total} perPage={perPage} onPageChange={setPage} />
          </>
        )}
      </div>

      {/* User Detail Modal */}
      {detailUser && (
        <div className="modal-overlay" onClick={() => setDetailUser(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{detailUser.username}</h2>
              <button className="modal-close" onClick={() => setDetailUser(null)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-field"><div className="detail-label">ID</div><div className="detail-value">#{detailUser.id}</div></div>
                <div className="detail-field"><div className="detail-label">Username</div><div className="detail-value">{detailUser.username}</div></div>
                <div className="detail-field"><div className="detail-label">Email</div><div className="detail-value">{detailUser.email}</div></div>
                <div className="detail-field"><div className="detail-label">Name</div><div className="detail-value">{detailUser.first_name} {detailUser.last_name}</div></div>
                <div className="detail-field"><div className="detail-label">Phone</div><div className="detail-value">{detailUser.phone || 'N/A'}</div></div>
                <div className="detail-field"><div className="detail-label">Role</div><div className="detail-value"><span className={`badge badge-${detailUser.role}`}>{detailUser.role}</span></div></div>
                <div className="detail-field"><div className="detail-label">Status</div><div className="detail-value"><span className={`badge ${detailUser.is_active ? 'badge-active' : 'badge-inactive'}`}>{detailUser.is_active ? 'Active' : 'Inactive'}</span></div></div>
                <div className="detail-field"><div className="detail-label">Verified</div><div className="detail-value">{detailUser.is_verified ? 'Yes' : 'No'}</div></div>
                <div className="detail-field"><div className="detail-label">Joined</div><div className="detail-value">{new Date(detailUser.created_at).toLocaleString()}</div></div>
              </div>
            </div>
            {isAdmin && detailUser.id !== user?.id && (
              <div className="modal-footer">
                <button className="btn btn-danger" onClick={() => setConfirmDelete(detailUser.id)}>Delete</button>
                <select className="filter-select" value={detailUser.role} onChange={e => handleRoleUpdate(detailUser.id, e.target.value)}>
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="user">User</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      <ConfirmDialog open={!!confirmDelete} title="Delete User"
        message="Are you sure you want to delete this user?"
        onConfirm={() => handleDelete(confirmDelete)} onCancel={() => setConfirmDelete(null)} />
      <ConfirmDialog open={confirmBulkDelete} title="Bulk Delete"
        message={`Delete ${selected.length} selected users?`}
        onConfirm={handleBulkDelete} onCancel={() => setConfirmBulkDelete(false)} />
    </div>
  );
}
