export default function Pagination({ page, pages, onPageChange }) {
  if (pages <= 1) return null

  const getPageNumbers = () => {
    const nums = []
    const delta = 2
    for (let i = Math.max(1, page - delta); i <= Math.min(pages, page + delta); i++) {
      nums.push(i)
    }
    return nums
  }

  return (
    <div className="pagination">
      <button className="page-btn" onClick={() => onPageChange(page - 1)} disabled={page === 1}>‹</button>
      {page > 3 && <><button className="page-btn" onClick={() => onPageChange(1)}>1</button><span style={{color:'var(--text-muted)'}}>…</span></>}
      {getPageNumbers().map(n => (
        <button
          key={n}
          className={`page-btn ${n === page ? 'page-btn--active' : ''}`}
          onClick={() => onPageChange(n)}
        >{n}</button>
      ))}
      {page < pages - 2 && <><span style={{color:'var(--text-muted)'}}>…</span><button className="page-btn" onClick={() => onPageChange(pages)}>{pages}</button></>}
      <button className="page-btn" onClick={() => onPageChange(page + 1)} disabled={page === pages}>›</button>
    </div>
  )
}
