import React from 'react';

export default function EmptyState({ icon = '📭', title = 'No data found', message = 'There are no items to display at the moment.', action, actionLabel }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{message}</p>
      {action && (
        <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={action}>
          {actionLabel || 'Get Started'}
        </button>
      )}
    </div>
  );
}
