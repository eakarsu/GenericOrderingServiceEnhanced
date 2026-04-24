import React from 'react';

export default function Pagination({ page, totalPages, total, perPage, onPageChange }) {
  const start = (page - 1) * perPage + 1;
  const end = Math.min(page * perPage, total);

  const pages = [];
  const maxVisible = 5;
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);
  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }
  for (let i = startPage; i <= endPage; i++) pages.push(i);

  return (
    <div className="pagination">
      <div className="pagination-info">
        Showing {total > 0 ? start : 0} to {end} of {total} results
      </div>
      <div className="pagination-buttons">
        <button disabled={page <= 1} onClick={() => onPageChange(1)}>First</button>
        <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Prev</button>
        {startPage > 1 && <button disabled>...</button>}
        {pages.map(p => (
          <button key={p} className={p === page ? 'active' : ''} onClick={() => onPageChange(p)}>
            {p}
          </button>
        ))}
        {endPage < totalPages && <button disabled>...</button>}
        <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
        <button disabled={page >= totalPages} onClick={() => onPageChange(totalPages)}>Last</button>
      </div>
    </div>
  );
}
