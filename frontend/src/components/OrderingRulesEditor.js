import React, { useEffect, useState } from 'react';

const FIELDS = ['total', 'item_count', 'status', 'sector', 'user_role'];
const OPERATORS = ['>', '>=', '<', '<=', '==', '!=', 'in', 'contains'];
const ACTIONS = ['allow', 'warn', 'block'];

const ACTION_COLORS = {
  allow: { bg: '#dcfce7', fg: '#166534' },
  warn: { bg: '#fef3c7', fg: '#92400e' },
  block: { bg: '#fee2e2', fg: '#991b1b' },
};

const EMPTY = { name: '', field: 'total', operator: '>=', value: '', action: 'allow', enabled: true };

export default function OrderingRulesEditor({ user }) {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [draft, setDraft] = useState(EMPTY);
  const [editingId, setEditingId] = useState(null);
  const [busy, setBusy] = useState(false);

  const canEdit = !user || user.role === 'admin' || user.role === 'manager';

  function auth() {
    return { Authorization: `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' };
  }

  async function load() {
    setLoading(true); setErr(null);
    try {
      const r = await fetch('/api/custom-views/ordering-rules', { headers: auth() });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setRules(d.rules || []);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function save() {
    if (!draft.name.trim() || !draft.value.toString().trim()) {
      setErr('Name and value are required.');
      return;
    }
    setBusy(true); setErr(null);
    try {
      const url = editingId
        ? `/api/custom-views/ordering-rules/${editingId}`
        : '/api/custom-views/ordering-rules';
      const method = editingId ? 'PUT' : 'POST';
      const r = await fetch(url, { method, headers: auth(), body: JSON.stringify(draft) });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.detail || `HTTP ${r.status}`);
      }
      setDraft(EMPTY); setEditingId(null);
      await load();
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  async function remove(id) {
    if (!confirm('Delete this ordering rule?')) return;
    setBusy(true); setErr(null);
    try {
      const r = await fetch(`/api/custom-views/ordering-rules/${id}`, { method: 'DELETE', headers: auth() });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.detail || `HTTP ${r.status}`);
      }
      await load();
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  function startEdit(r) {
    setEditingId(r.id);
    setDraft({ name: r.name, field: r.field, operator: r.operator, value: r.value, action: r.action, enabled: r.enabled });
  }

  function cancelEdit() {
    setEditingId(null);
    setDraft(EMPTY);
    setErr(null);
  }

  return (
    <div data-testid="ordering-rules-editor" style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Ordering Rules Editor</h3>
          <p style={{ margin: '2px 0 0', color: '#64748b', fontSize: 12 }}>
            Define validation/policy rules applied to incoming orders. {canEdit ? '' : '(read-only — manager/admin to edit)'}
          </p>
        </div>
        <span style={{ background: '#eff6ff', color: '#1d4ed8', padding: '4px 10px', borderRadius: 999, fontSize: 12, fontWeight: 600 }}>
          {rules.length} rule{rules.length === 1 ? '' : 's'}
        </span>
      </div>

      {canEdit && (
        <div style={{ background: '#f8fafc', padding: 14, borderRadius: 8, marginBottom: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.2fr 0.9fr 1.2fr 1fr', gap: 8, marginBottom: 8 }}>
            <input
              data-testid="rule-name"
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="Rule name"
              style={inp}
            />
            <select data-testid="rule-field" value={draft.field} onChange={(e) => setDraft({ ...draft, field: e.target.value })} style={inp}>
              {FIELDS.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
            <select data-testid="rule-operator" value={draft.operator} onChange={(e) => setDraft({ ...draft, operator: e.target.value })} style={inp}>
              {OPERATORS.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
            <input
              data-testid="rule-value"
              value={draft.value}
              onChange={(e) => setDraft({ ...draft, value: e.target.value })}
              placeholder="Value"
              style={inp}
            />
            <select data-testid="rule-action" value={draft.action} onChange={(e) => setDraft({ ...draft, action: e.target.value })} style={inp}>
              {ACTIONS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#475569' }}>
              <input type="checkbox" checked={draft.enabled} onChange={(e) => setDraft({ ...draft, enabled: e.target.checked })} />
              Enabled
            </label>
            <div style={{ flex: 1 }} />
            {editingId && (
              <button onClick={cancelEdit} style={btnGhost}>Cancel</button>
            )}
            <button data-testid="rule-save" onClick={save} disabled={busy} style={btnPrimary}>
              {busy ? 'Saving…' : editingId ? 'Update Rule' : 'Add Rule'}
            </button>
          </div>
        </div>
      )}

      {err && <div style={{ padding: '8px 12px', background: '#fee2e2', color: '#991b1b', borderRadius: 6, fontSize: 13, marginBottom: 12 }}>Error: {err}</div>}

      {loading ? (
        <div style={{ padding: 16 }}>Loading rules…</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
                <th style={th}>Name</th>
                <th style={th}>Field</th>
                <th style={th}>Op</th>
                <th style={th}>Value</th>
                <th style={th}>Action</th>
                <th style={th}>Enabled</th>
                {canEdit && <th style={{ ...th, textAlign: 'right' }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {rules.length === 0 && (
                <tr><td colSpan={canEdit ? 7 : 6} style={{ padding: 16, color: '#94a3b8', textAlign: 'center' }}>No rules defined.</td></tr>
              )}
              {rules.map((r) => {
                const ac = ACTION_COLORS[r.action] || ACTION_COLORS.allow;
                return (
                  <tr key={r.id} data-testid={`rule-row-${r.id}`} style={{ borderTop: '1px solid #e2e8f0' }}>
                    <td style={td}><b>{r.name}</b></td>
                    <td style={td}><code style={code}>{r.field}</code></td>
                    <td style={td}><code style={code}>{r.operator}</code></td>
                    <td style={td}><code style={code}>{r.value}</code></td>
                    <td style={td}>
                      <span style={{ background: ac.bg, color: ac.fg, padding: '2px 8px', borderRadius: 999, fontWeight: 600, fontSize: 12 }}>
                        {r.action}
                      </span>
                    </td>
                    <td style={td}>{r.enabled ? 'Yes' : 'No'}</td>
                    {canEdit && (
                      <td style={{ ...td, textAlign: 'right' }}>
                        <button onClick={() => startEdit(r)} style={btnGhost}>Edit</button>
                        <button onClick={() => remove(r.id)} style={{ ...btnGhost, color: '#dc2626', marginLeft: 6 }}>Delete</button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const inp = { padding: '8px 10px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: 13, background: '#fff' };
const th = { padding: '10px 12px', fontSize: 12, color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.4 };
const td = { padding: '10px 12px', color: '#0f172a' };
const code = { background: '#f1f5f9', padding: '2px 6px', borderRadius: 4, fontSize: 12, color: '#1e293b' };
const btnPrimary = { padding: '8px 16px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer', fontSize: 13 };
const btnGhost = { padding: '6px 12px', background: 'transparent', border: '1px solid #cbd5e1', borderRadius: 6, color: '#475569', cursor: 'pointer', fontSize: 12, fontWeight: 600 };
