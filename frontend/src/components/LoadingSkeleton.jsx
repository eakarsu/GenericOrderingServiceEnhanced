import React from 'react';

export function SkeletonCards({ count = 6 }) {
  return (
    <div className="cards-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton skeleton-card" />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 5 }) {
  return (
    <div className="table-container">
      <div style={{ padding: '1rem 1.25rem' }}>
        <div className="skeleton skeleton-text" style={{ width: '250px', height: '2rem' }} />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton skeleton-row" style={{ margin: '0 1.25rem' }} />
      ))}
      <div style={{ padding: '1rem 1.25rem' }}>
        <div className="skeleton skeleton-text short" />
      </div>
    </div>
  );
}

export function SkeletonDetail() {
  return (
    <div style={{ padding: '1.5rem' }}>
      <div className="skeleton skeleton-text" style={{ width: '60%', height: '1.5rem', marginBottom: '1.5rem' }} />
      <div className="detail-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i}>
            <div className="skeleton skeleton-text short" style={{ height: '0.75rem' }} />
            <div className="skeleton skeleton-text" style={{ height: '1rem' }} />
          </div>
        ))}
      </div>
    </div>
  );
}
