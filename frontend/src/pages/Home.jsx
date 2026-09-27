import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { postsApi } from '../api/posts'
import { usersApi } from '../api/users'
import { useAuth } from '../context/AuthContext'
import PostCard from '../components/PostCard'
import Pagination from '../components/Pagination'

export default function Home() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const [activeTag, setActiveTag] = useState('')
  const { user } = useAuth()

  const search = searchParams.get('search') || ''

  const { data, isLoading, isError } = useQuery({
    queryKey: ['posts', page, search, activeTag],
    queryFn: () => postsApi.list({ page, limit: 9, search, tag: activeTag }).then(r => r.data),
    keepPreviousData: true,
  })

  const { data: draftsData } = useQuery({
    queryKey: ['user-drafts'],
    queryFn: () => usersApi.getPosts().then(r => r.data),
    enabled: !!user,
  })

  const drafts = draftsData?.items?.filter(post => post.status === 'draft') || []

  const handleTagClick = (tag) => {
    setActiveTag(prev => prev === tag ? '' : tag)
    setPage(1)
  }

  const clearSearch = () => {
    setSearchParams({})
    setPage(1)
  }

  const clearTag = () => {
    setActiveTag('')
    setPage(1)
  }

  const showFeatured = page === 1 && !search && !activeTag
  const featured = showFeatured ? data?.items?.[0] : null
  const rest = featured ? data.items.slice(1) : (data?.items || [])

  return (
    <main className="page">
      <div className="container">
        <section className="hero hero--editorial">
          <div className="hero__stamp" aria-hidden="true">Vol. 01</div>
          <div className="hero__copy">
            <p className="hero__eyebrow">Field notes</p>
            <h1 className="hero__title">Ideas with a <em>pulse.</em></h1>
            <p className="hero__subtitle">Sharp takes, field notes, and deep dives from people who actually ship.</p>
            {user ? (
              <Link to="/create" className="btn btn--primary">New post</Link>
            ) : (
              <Link to="/register" className="btn btn--primary">Get started</Link>
            )}
          </div>
        </section>

        {(search || activeTag) && (
          <div className="filters">
            {search && <span className="tag">Search: "{search}" <button onClick={clearSearch} style={{background:'none',border:'none',cursor:'pointer',color:'inherit',marginLeft:'4px'}}>×</button></span>}
            {activeTag && <span className="tag">#{activeTag} <button onClick={clearTag} style={{background:'none',border:'none',cursor:'pointer',color:'inherit',marginLeft:'4px'}}>×</button></span>}
          </div>
        )}

        {isLoading && <div className="loading-page"><div className="spinner" /></div>}
        {isError && <div className="empty-state"><div className="empty-state__icon">😕</div><p className="empty-state__title">Failed to load posts</p></div>}

        {user && drafts.length > 0 && (
          <section className="home-section">
            <div className="section-header">
              <h2 className="section-title">Your drafts</h2>
              <span className="text-muted">{drafts.length} unpublished</span>
            </div>
            <div className="post-grid">
              {drafts.map(post => (
                <PostCard
                  key={post.id || post._id}
                  post={post}
                  onTagClick={handleTagClick}
                />
              ))}
            </div>
          </section>
        )}

        {data && (
          <>
            <div className="section-header">
              <h2 className="section-title">{search || activeTag ? 'Results' : 'Latest'}</h2>
              <span className="text-muted">{data.total} articles</span>
            </div>
            {data.items.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state__icon">📭</div>
                <h2 className="empty-state__title">No posts found</h2>
                <p className="empty-state__text">Try a different search or check back later.</p>
              </div>
            ) : (
              <>
                {featured && (
                  <div className="featured-wrap">
                    <PostCard
                      post={featured}
                      featured
                      onTagClick={handleTagClick}
                      searchTerm={search}
                    />
                  </div>
                )}
                {rest.length > 0 && (
                  <div className="post-grid">
                    {rest.map(post => (
                      <PostCard
                        key={post.id}
                        post={post}
                        onTagClick={handleTagClick}
                        searchTerm={search}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
            <Pagination page={data.page} pages={data.pages} onPageChange={setPage} />
          </>
        )}
      </div>
    </main>
  )
}
