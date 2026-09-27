import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { readingHistoryApi } from '../api/readingHistory'
import { useAuth } from '../context/AuthContext'
import AvatarPlaceholder from '../components/AvatarPlaceholder'
import CoverVisual from '../components/CoverVisual'

export default function ReadingHistory() {
  const { user } = useAuth()
  const [page, setPage] = useState(1)

  const { data: historyData, isLoading } = useQuery({
    queryKey: ['reading-history', page],
    queryFn: () => readingHistoryApi.getHistory({ limit: 20, offset: (page - 1) * 20 }).then(r => r.data),
    enabled: !!user,
  })

  const { data: statsData } = useQuery({
    queryKey: ['reading-stats'],
    queryFn: () => readingHistoryApi.getStats().then(r => r.data),
    enabled: !!user,
  })

  const history = historyData?.items || []
  const stats = statsData || {}

  if (!user) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <h2>Please log in to view your reading history</h2>
        <Link to="/login" className="btn btn--primary" style={{ marginTop: '1rem' }}>
          Login
        </Link>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
        <p className="text-muted">Loading reading history...</p>
      </div>
    )
  }

  return (
    <main className="page">
      <div className="container">
        <div className="history-hero">
          <h1 className="history-hero__title">Reading history</h1>
          <p className="text-muted">Posts you have opened recently, kept in one place.</p>
        </div>

        {/* Stats Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--accent)' }}>{stats.total_reads || 0}</div>
            <div className="text-muted">Total Reads</div>
          </div>
          <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--accent)' }}>{stats.unique_posts || 0}</div>
            <div className="text-muted">Unique Articles</div>
          </div>
          <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--accent)' }}>{stats.top_tags?.length || 0}</div>
            <div className="text-muted">Topics Explored</div>
          </div>
        </div>

        {/* Top Tags */}
        {stats.top_tags && stats.top_tags.length > 0 && (
          <div style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>Most Read Topics</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              {stats.top_tags.map((tag, index) => (
                <span
                  key={tag.name}
                  className="tag"
                  style={{
                    fontSize: `${1.2 - index * 0.1}rem`,
                    opacity: `${1 - index * 0.1}`,
                  }}
                >
                  #{tag.name} ({tag.count})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Reading Timeline */}
        <div>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Reading Timeline</h2>
          {history.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">📚</div>
              <h2 className="empty-state__title">No reading history yet</h2>
              <p className="empty-state__text">Start exploring articles to build your reading fingerprint!</p>
              <Link to="/" className="btn btn--primary" style={{ marginTop: '1rem' }}>
                Browse Articles
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {history.map((item) => (
                <Link key={item.id} to={`/posts/${item.post_id}`} className="history-row">
                  <CoverVisual
                    className="history-row__cover"
                    post={{
                      id: item.post_id,
                      title: item.post_title,
                      cover_image_url: item.cover_image_url,
                    }}
                  />
                  <div className="history-row__body">
                    <h3 className="history-row__title">{item.post_title}</h3>
                    <div className="history-row__meta">
                      <AvatarPlaceholder name={item.author?.name || 'Anonymous'} size="sm" />
                      <span>{item.author?.name || 'Anonymous'}</span>
                      <span className="text-muted">
                        {formatDistanceToNow(new Date(item.read_at), { addSuffix: true })}
                      </span>
                    </div>
                    {item.tags && item.tags.length > 0 && (
                      <div className="post-card__tags">
                        {item.tags.map((tag) => {
                          const tagName = typeof tag === 'object' ? tag.name : tag
                          return (
                            <span key={tagName} className="tag">
                              #{tagName}
                            </span>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
