import React from 'react';

export default function ConfirmDialog({ open, title, message, confirmText = 'Confirm', cancelText = 'Cancel', variant = 'danger', onConfirm, onCancel }) {
  if (!open) return null;

  const btnClass = variant === 'danger' ? 'btn-danger' : 'btn-primary';
  const icon = variant === 'danger' ? '&#9888;' : '&#10067;';

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" style={{ maxWidth: '420px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-body">
          <div className="confirm-body">
            <div className="confirm-icon" dangerouslySetInnerHTML={{ __html: icon }} />
            <h3>{title}</h3>
            <p>{message}</p>
          </div>
        </div>
        <div className="modal-footer" style={{ justifyContent: 'center' }}>
          <button className="btn btn-outline" onClick={onCancel}>{cancelText}</button>
          <button className={`btn ${btnClass}`} onClick={onConfirm}>{confirmText}</button>
        </div>
      </div>
    </div>
  );
}
