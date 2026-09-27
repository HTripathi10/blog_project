import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { postsApi } from '../api/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function LikeButton({ liked: initialLiked, count: initialCount, postId, onToggle }) {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [liked, setLiked] = useState(initialLiked ?? false)
  const [count, setCount] = useState(initialCount ?? 0)
  const [loading, setLoading] = useState(false)

  // Sync local state with props when they change (e.g., after data refresh)
  useEffect(() => {
    setLiked(initialLiked ?? false)
    setCount(initialCount ?? 0)
  }, [initialLiked, initialCount])

  const toggleMutation = useMutation({
    mutationFn: () => postsApi.toggleLike(postId),
    onSuccess: (res) => {
      const data = res.data
      setLiked(data.liked)
      setCount(data.like_count)
      // Invalidate posts queries to update like counts across the app
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      queryClient.invalidateQueries({ queryKey: ['post', postId] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['user-drafts'] })
      onToggle?.(postId, data)
    },
    onError: () => {
      toast.error('Failed to update like')
    },
  })

  const handleToggle = async () => {
    if (!isAuthenticated) {
      toast.error('Login to like posts')
      return
    }
    if (loading) return
    setLoading(true)
    try {
      await toggleMutation.mutateAsync()
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      className={`like-btn ${liked ? 'like-btn--liked' : ''}`}
      onClick={handleToggle}
      disabled={loading}
      aria-label={liked ? 'Unlike' : 'Like'}
    >
      <span className="like-btn__icon">{liked ? '❤️' : '🤍'}</span>
      <span>{count}</span>
    </button>
  )
}
