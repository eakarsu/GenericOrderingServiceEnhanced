const BASE = '/api';

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('token');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    ...options,
    headers: { ...getHeaders(), ...options.headers }
  });
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  if (res.headers.get('content-type')?.includes('text/csv') || res.headers.get('content-type')?.includes('text/html')) {
    return res;
  }
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || data.message || 'Request failed');
  return data;
}

export const api = {
  // Auth
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me'),
  resetPasswordRequest: (data) => request('/auth/password-reset/request', { method: 'POST', body: JSON.stringify(data) }),
  resetPasswordConfirm: (data) => request('/auth/password-reset/confirm', { method: 'POST', body: JSON.stringify(data) }),
  changePassword: (data) => request('/auth/change-password', { method: 'POST', body: JSON.stringify(data) }),
  verifyEmail: (token) => request(`/auth/verify-email/${token}`, { method: 'POST' }),

  // Users
  getUsers: (params) => request(`/users/?${new URLSearchParams(params)}`),
  getUser: (id) => request(`/users/${id}`),
  updateProfile: (data) => request('/users/profile', { method: 'PUT', body: JSON.stringify(data) }),
  updateSettings: (data) => request('/users/settings', { method: 'PUT', body: JSON.stringify(data) }),
  getSettings: () => request('/users/settings/me'),
  updateUserRole: (id, data) => request(`/users/${id}/role`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (id) => request(`/users/${id}`, { method: 'DELETE' }),
  bulkDeleteUsers: (ids) => request('/users/bulk-delete', { method: 'POST', body: JSON.stringify({ ids }) }),
  bulkUpdateUsers: (ids, updates) => request('/users/bulk-update', { method: 'POST', body: JSON.stringify({ ids, updates }) }),

  // Sectors
  getSectors: (params) => request(`/sectors/?${new URLSearchParams(params)}`),
  getSector: (id) => request(`/sectors/${id}`),
  getSectorBySlug: (slug) => request(`/sectors/slug/${slug}`),

  // Items
  getItems: (params) => request(`/items/?${new URLSearchParams(params)}`),
  getItem: (id) => request(`/items/${id}`),
  createItem: (sectorId, data) => request(`/items/sector/${sectorId}`, { method: 'POST', body: JSON.stringify(data) }),
  updateItem: (id, data) => request(`/items/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteItem: (id) => request(`/items/${id}`, { method: 'DELETE' }),
  bulkDeleteItems: (ids) => request('/items/bulk-delete', { method: 'POST', body: JSON.stringify({ ids }) }),
  bulkUpdateItems: (ids, updates) => request('/items/bulk-update', { method: 'POST', body: JSON.stringify({ ids, updates }) }),

  // Orders
  getOrders: (params) => request(`/orders/?${new URLSearchParams(params)}`),
  getOrder: (id) => request(`/orders/${id}`),
  createOrder: (data) => request('/orders/', { method: 'POST', body: JSON.stringify(data) }),
  updateOrder: (id, data) => request(`/orders/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteOrder: (id) => request(`/orders/${id}`, { method: 'DELETE' }),
  bulkDeleteOrders: (ids) => request('/orders/bulk-delete', { method: 'POST', body: JSON.stringify({ ids }) }),
  bulkUpdateOrders: (ids, updates) => request('/orders/bulk-update', { method: 'POST', body: JSON.stringify({ ids, updates }) }),

  // Export
  exportItemsCsv: (params = {}) => request(`/export/items/csv?${new URLSearchParams(params)}`),
  exportOrdersCsv: (params = {}) => request(`/export/orders/csv?${new URLSearchParams(params)}`),
  exportUsersCsv: () => request('/export/users/csv'),
  exportItemsPdf: (params = {}) => request(`/export/items/pdf?${new URLSearchParams(params)}`),
  exportOrdersPdf: (params = {}) => request(`/export/orders/pdf?${new URLSearchParams(params)}`),

  // Stats
  getStats: () => request('/stats'),
};

export async function downloadExport(url, filename) {
  const res = await fetch(`${BASE}${url}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Export failed');
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
