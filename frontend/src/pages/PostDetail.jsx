import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'
import { formatDistanceToNow, format } from 'date-fns'
import { postsApi } from '../api/posts'
import { readingHistoryApi } from '../api/readingHistory'
import { useAuth } from '../context/AuthContext'
import AvatarPlaceholder from '../components/AvatarPlaceholder'
import LikeButton from '../components/LikeButton'
import CommentSection from '../components/CommentSection'
import CoverVisual from '../components/CoverVisual'
import toast from 'react-hot-toast'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const hasRecorded = useRef(false)

  const { data: post, isLoading, isError, error } = useQuery({
    queryKey: ['post', id],
    queryFn: async () => {
      const res = await postsApi.get(id)
      return res.data
    },
  })

  // Record reading history when user views a post (only once per page load)
  const recordReadingMutation = useMutation({
    mutationFn: () => readingHistoryApi.recordReading(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reading-history'] })
      queryClient.invalidateQueries({ queryKey: ['reading-stats'] })
    },
  })

  useEffect(() => {
    if (user && post && !hasRecorded.current) {
      // Don't count if user is the author of the post
      const isAuthor = post.user_id === user.id || post.author?.id === user.id
      if (!isAuthor) {
        hasRecorded.current = true
        recordReadingMutation.mutate()
      }
    }
  }, [user, post, recordReadingMutation])

  const deleteMutation = useMutation({
    mutationFn: () => postsApi.delete(id),
    onSuccess: () => {
      toast.success('Post deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      navigate('/')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to delete post')
    },
  })

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
      deleteMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
        <p className="text-muted">Loading article...</p>
      </div>
    )
  }

  if (isError || !post) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <h2 style={{ marginBottom: '1rem' }}>Post not found</h2>
        <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
          {error?.response?.data?.message || "The article you're looking for doesn't exist or was removed."}
        </p>
        <Link to="/" className="btn btn-primary">
          Back to Articles
        </Link>
      </div>
    )
  }

  const isAuthor = user && post.author && user.id === post.author.id

  const authorName = post.author?.name || 'Anonymous'
  const publishedAt = post.created_at || post.createdAt
  const minutes = post.reading_time_minutes || post.readingTime || Math.max(1, Math.ceil((post.content?.replace(/<[^>]+>/g, '').split(/\s+/).length || 0) / 200))

  return (
    <div className="post-detail-page container">
      <div className="post-detail-header">
        <Link to="/" className="back-link">
          ← Back to home
        </Link>

        {post.tags && post.tags.length > 0 && (
          <div className="post-tags" style={{ marginTop: '1rem' }}>
            {post.tags.map((tag) => {
              const tagName = typeof tag === 'object' ? tag.name : tag
              const tagKey = typeof tag === 'object' ? tag.id || tag.name : tag
              return (
                <span key={tagKey} className="tag-badge">
                  #{tagName}
                </span>
              )
            })}
          </div>
        )}

        <h1 className="post-detail-title">{post.title}</h1>

        <div className="post-detail-meta">
          <div className="post-author-wrapper">
            {post.author?.avatar_url ? (
              <img src={post.author.avatar_url} alt={authorName} className="avatar avatar--md" referrerPolicy="no-referrer" />
            ) : (
              <AvatarPlaceholder name={authorName} size="md" />
            )}
            <div className="post-author-details">
              <span className="author-name">{authorName}</span>
              <div className="post-date-info">
                <span>
                  {publishedAt ? format(new Date(publishedAt), 'MMMM dd, yyyy') : ''}
                </span>
                <span>•</span>
                <span>{minutes} min read</span>
              </div>
            </div>
          </div>

          <div className="post-detail-actions">
            <LikeButton
              postId={post.id || id}
              liked={post.is_liked_by_me}
              count={post.like_count}
            />

            {isAuthor && (
              <div className="author-controls">
                <Link to={`/posts/${id}/edit`} className="btn btn-secondary btn-sm">
                  Edit
                </Link>
                <button
                  onClick={handleDelete}
                  className="btn btn-danger btn-sm"
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            )}
          </div>
        </div>

        {post.cover_image_url && (
          <div className="post-cover-image">
            <CoverVisual post={post} />
          </div>
        )}
      </div>

      <article className="post-content editor-content markdown-body">
        <div dangerouslySetInnerHTML={{ __html: post.content || '' }} />
      </article>

      {post.status !== 'draft' && (
        <>
          <hr className="divider" />
          <CommentSection postId={post._id || id} />
        </>
      )}
    </div>
  )
}
