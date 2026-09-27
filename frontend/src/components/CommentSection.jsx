import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'
import { postsApi } from '../api/posts'
import { useAuth } from '../context/AuthContext'
import AvatarPlaceholder from './AvatarPlaceholder'
import toast from 'react-hot-toast'

export default function CommentSection({ postId }) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [content, setContent] = useState('')

  const { data: comments = [], isLoading } = useQuery({
    queryKey: ['comments', postId],
    queryFn: async () => {
      const res = await postsApi.listComments(postId)
      return res.data
    },
  })

  const addMutation = useMutation({
    mutationFn: (content) => postsApi.addComment(postId, { content }),
    onSuccess: () => {
      setContent('')
      queryClient.invalidateQueries({ queryKey: ['comments', postId] })
      toast.success('Comment posted!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to post comment')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (commentId) => postsApi.deleteComment(postId, commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', postId] })
      toast.success('Comment deleted')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to delete comment')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!content.trim()) return
    addMutation.mutate(content.trim())
  }

  return (
    <section className="comment-section">
      <h3 className="section-title">
        Discussion ({comments.length})
      </h3>

      {user ? (
        <form onSubmit={handleSubmit} className="comment-form">
          <div className="comment-form-avatar">
            <AvatarPlaceholder name={user.name || user.email} size="sm" />
          </div>
          <div className="comment-form-body">
            <textarea
              className="comment-input"
              placeholder="Share your thoughts or ask a question..."
              rows={3}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={addMutation.isPending}
            />
            <div className="comment-form-actions">
              <button
                type="submit"
                className="btn btn-primary btn-sm"
                disabled={!content.trim() || addMutation.isPending}
              >
                {addMutation.isPending ? 'Posting...' : 'Post Comment'}
              </button>
            </div>
          </div>
        </form>
      ) : (
        <div className="comment-login-prompt">
          <p>
            Please <Link to="/login" className="link">sign in</Link> to join the discussion.
          </p>
        </div>
      )}

      {isLoading ? (
        <div className="comment-loading">
          <div className="spinner-sm"></div>
          <span>Loading comments...</span>
        </div>
      ) : comments.length === 0 ? (
        <div className="empty-state">
          <p>No comments yet. Be the first to start the conversation!</p>
        </div>
      ) : (
        <div className="comment-list">
          {comments.map((comment) => {
            const isAuthor = user && (user._id === comment.author?._id || user.id === comment.author?._id || user._id === comment.author || user.id === comment.author)
            const authorName = comment.author?.name || 'Anonymous'

            return (
              <div key={comment._id} className="comment-item">
                <div className="comment-header">
                  <div className="comment-author-info">
                    <AvatarPlaceholder name={authorName} size="sm" />
                    <div>
                      <span className="comment-author-name">{authorName}</span>
                      <span className="comment-time">
                        {comment.createdAt
                          ? formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })
                          : 'just now'}
                      </span>
                    </div>
                  </div>
                  {isAuthor && (
                    <button
                      onClick={() => {
                        if (confirm('Delete this comment?')) {
                          deleteMutation.mutate(comment._id)
                        }
                      }}
                      className="btn-icon text-danger"
                      title="Delete comment"
                      disabled={deleteMutation.isPending}
                    >
                      🗑️
                    </button>
                  )}
                </div>
                <div className="comment-body">
                  <p>{comment.body || comment.content}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
