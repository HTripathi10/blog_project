import { useNavigate } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import AvatarPlaceholder from './AvatarPlaceholder'
import LikeButton from './LikeButton'
import CoverVisual from './CoverVisual'
import { highlightText } from '../utils/highlightText'

export default function PostCard({ post, onTagClick, searchTerm, featured = false }) {
  const navigate = useNavigate()
  if (!post) return null

  const excerpt = (post.content || '').replace(/<[^>]+>/g, '').replace(/[#*`[\]()!_>~]/g, '').slice(0, featured ? 240 : 140)
  const authorName = post.author?.name || 'Anonymous'
  const avatarUrl = post.author?.avatar_url
  const postId = post.id || post._id

  let formattedDate = ''
  try {
    const dateField = post.created_at || post.createdAt
    if (dateField) {
      formattedDate = formatDistanceToNow(new Date(dateField), { addSuffix: true })
    }
  } catch {
    formattedDate = 'recently'
  }

  const highlightedTitle = highlightText(post.title || 'Untitled Post', searchTerm)
  const highlightedExcerpt = highlightText(excerpt, searchTerm)
  const highlightedAuthor = highlightText(authorName, searchTerm)

  return (
    <article
      className={`card post-card ${featured ? 'post-card--featured' : ''}`}
      onClick={() => navigate(`/posts/${postId}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && navigate(`/posts/${postId}`)}
    >
      <div className="post-card__cover">
        <CoverVisual post={post} />
      </div>

      <div className="post-card__body">
        <div className="post-card__meta">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={authorName}
              className="post-card__avatar"
              referrerPolicy="no-referrer"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          ) : (
            <AvatarPlaceholder name={authorName} size="sm" />
          )}
          <div>
            <div className="post-card__author" dangerouslySetInnerHTML={{ __html: highlightedAuthor }}></div>
            <div className="post-card__date">{formattedDate}</div>
          </div>
          {post.status === 'draft' && (
            <span className="tag tag--draft" style={{ marginLeft: 'auto' }}>
              Draft
            </span>
          )}
        </div>

        {featured && <p className="post-card__kicker">Featured</p>}

        <h2 className="post-card__title" dangerouslySetInnerHTML={{ __html: highlightedTitle }}></h2>

        {post.tags && post.tags.length > 0 && (
          <div className="post-card__tags">
            {post.tags.map((tag) => {
              const tagName = typeof tag === 'object' ? tag.name : tag
              const tagKey = typeof tag === 'object' ? tag.id || tag.name : tag
              const highlightedTag = highlightText(tagName, searchTerm)
              return (
                <span
                  key={tagKey}
                  className="tag"
                  onClick={(e) => {
                    if (onTagClick) {
                      e.stopPropagation()
                      onTagClick(tagName)
                    }
                  }}
                  dangerouslySetInnerHTML={{ __html: `#${highlightedTag}` }}
                />
              )
            })}
          </div>
        )}

        <p className="post-card__excerpt" dangerouslySetInnerHTML={{ __html: highlightedExcerpt + (excerpt.length >= (featured ? 240 : 140) ? '...' : '') }}></p>

        <div className="post-card__footer">
          <div className="post-card__stats">
            <span className="post-card__stat reading-time">
              {post.reading_time_minutes || 1} min read
            </span>
            <span className="post-card__stat">
              {post.comment_count || 0} comments
            </span>
          </div>
          <div onClick={(e) => e.stopPropagation()}>
            <LikeButton
              liked={post.is_liked_by_me}
              count={post.like_count || 0}
              postId={postId}
            />
          </div>
        </div>
      </div>
    </article>
  )
}
