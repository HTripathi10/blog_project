import { useState } from 'react'
import { useParams, Link, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { usersApi } from '../api/users'
import { useAuth } from '../context/AuthContext'
import AvatarPlaceholder from '../components/AvatarPlaceholder'
import PostCard from '../components/PostCard'
import toast from 'react-hot-toast'

export default function Profile() {
  const { userId } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const { user: currentUser, updateUser } = useAuth()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [removingAvatar, setRemovingAvatar] = useState(false)
  const [avatarLoadError, setAvatarLoadError] = useState(false)

  const search = searchParams.get('search') || ''

  // Target ID is either from params or current logged in user
  const targetUserId = userId || currentUser?.id || currentUser?._id
  const isOwnProfile = !userId || String(userId) === String(currentUser?.id || currentUser?._id)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['profile', targetUserId],
    queryFn: async () => {
      if (!targetUserId) return null
      const res = await usersApi.getProfile(targetUserId)
      return res.data.data || res.data
    },
    enabled: Boolean(targetUserId),
  })

  const profileUser = data?.user || (isOwnProfile ? currentUser : null)
  const posts = data?.posts || []

  const filteredPosts = search
    ? posts.filter(post =>
        post.title?.toLowerCase().includes(search.toLowerCase()) ||
        post.content?.toLowerCase().includes(search.toLowerCase())
      )
    : posts

  const publishedPosts = filteredPosts.filter(post => post.status === 'published')
  const draftPosts = filteredPosts.filter(post => post.status === 'draft')

  const { register, handleSubmit } = useForm({
    values: {
      name: profileUser?.name || '',
      bio: profileUser?.bio || '',
    },
  })

  const updateMutation = useMutation({
    mutationFn: (formData) => usersApi.updateProfile(formData),
    onSuccess: (res) => {
      const updated = res.data.data || res.data
      toast.success('Profile updated!')
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['profile', targetUserId] })
      if (isOwnProfile && updateUser) {
        updateUser(updated)
      }
    },
    onError: (err) => {
      const detail = err.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : 'Failed to update profile')
    },
  })

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadingAvatar(true)
    try {
      const res = await usersApi.uploadAvatar(file)
      const updated = res.data.data || res.data
      toast.success('Avatar updated!')
      setAvatarLoadError(false)
      queryClient.invalidateQueries({ queryKey: ['profile', targetUserId] })
      if (isOwnProfile && updateUser) {
        updateUser(updated)
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : 'Failed to upload avatar')
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleAvatarRemove = async () => {
    setRemovingAvatar(true)
    try {
      const res = await usersApi.removeAvatar()
      const updated = res.data.data || res.data
      toast.success('Avatar removed')
      setAvatarLoadError(false)
      queryClient.invalidateQueries({ queryKey: ['profile', targetUserId] })
      if (isOwnProfile && updateUser) {
        updateUser(updated)
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : 'Failed to remove avatar')
    } finally {
      setRemovingAvatar(false)
    }
  }

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
        <p className="text-muted">Loading profile...</p>
      </div>
    )
  }

  if (isError || !profileUser) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <h2>User not found</h2>
        <p className="text-muted" style={{ marginTop: '0.5rem' }}>
          This user profile could not be loaded.
        </p>
        <Link to="/" className="btn btn--primary" style={{ marginTop: '1.5rem' }}>
          Back to Articles
        </Link>
      </div>
    )
  }

  const avatarUrl = profileUser.avatar_url
    ? profileUser.avatar_url.startsWith('http')
      ? profileUser.avatar_url
      : profileUser.avatar_url
    : null

  const showImg = Boolean(avatarUrl && !avatarLoadError)

  return (
    <div className="profile-page container">
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar-wrapper">
            <div className="profile-avatar-circle">
              {showImg ? (
                <img
                  src={avatarUrl}
                  alt={profileUser.name}
                  className="profile-avatar-img"
                  referrerPolicy="no-referrer"
                  onError={() => setAvatarLoadError(true)}
                />
              ) : (
                <AvatarPlaceholder name={profileUser.name || profileUser.email} size="xl" />
              )}
            </div>

            {isOwnProfile && (
              <label className="avatar-upload-btn" title="Change avatar photo">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  style={{ display: 'none' }}
                  disabled={uploadingAvatar || removingAvatar}
                />
                {uploadingAvatar ? '⏳' : '📷'}
              </label>
            )}
            {isOwnProfile && profileUser.avatar_url && (
              <button
                type="button"
                className="avatar-remove-btn"
                title="Remove avatar photo"
                aria-label="Remove avatar photo"
                onClick={handleAvatarRemove}
                disabled={uploadingAvatar || removingAvatar}
              >
                {removingAvatar ? '…' : '×'}
              </button>
            )}
          </div>

          <div className="profile-info">
            <div className="profile-name-row">
              <h1 className="profile-name">{profileUser.name}</h1>
              {isOwnProfile && !isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn btn--secondary btn--sm"
                >
                  Edit Profile
                </button>
              )}
            </div>
            <p className="profile-email text-muted">{profileUser.email}</p>
            {profileUser.bio && <p className="profile-bio">{profileUser.bio}</p>}
          </div>
        </div>

        {isEditing && (
          <form
            onSubmit={handleSubmit((formData) => updateMutation.mutate(formData))}
            className="profile-edit-form"
          >
            <div className="form-group">
              <label className="form-label" htmlFor="name">
                Name
              </label>
              <input id="name" type="text" className="input" {...register('name')} />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="bio">
                Bio
              </label>
              <textarea
                id="bio"
                className="input"
                rows={3}
                placeholder="Tell us a little bit about yourself..."
                {...register('bio')}
              />
            </div>

            <div className="profile-edit-actions">
              <button
                type="button"
                className="btn btn--secondary"
                onClick={() => setIsEditing(false)}
                disabled={updateMutation.isPending}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn--primary"
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        )}
      </div>

      {search && (
        <div className="filters" style={{ marginBottom: '2rem' }}>
          <span className="tag">🔍 "{search}" <button onClick={() => setSearchParams({})} style={{background:'none',border:'none',cursor:'pointer',color:'inherit',marginLeft:'4px'}}>×</button></span>
        </div>
      )}

      <div className="profile-posts-section">
        <div className="section-header">
          <h2 className="section-title">
            Published Articles ({publishedPosts.length})
          </h2>
        </div>

        {publishedPosts.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state__text">No published articles yet.</p>
            {isOwnProfile && (
              <Link to="/create" className="btn btn--primary" style={{ marginTop: '1rem' }}>
                Write your first article ✍️
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid--3">
            {publishedPosts.map((post) => (
              <PostCard key={post.id || post._id} post={post} searchTerm={search} />
            ))}
          </div>
        )}
      </div>

      {isOwnProfile && (
        <div className="profile-posts-section" style={{ marginTop: '3rem' }}>
          <h2 className="section-title">
            Drafts ({draftPosts.length})
          </h2>

          {draftPosts.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state__text">No drafts yet.</p>
              <Link to="/create" className="btn btn--primary" style={{ marginTop: '1rem' }}>
                Start writing ✍️
              </Link>
            </div>
          ) : (
            <div className="grid grid--3">
              {draftPosts.map((post) => (
                <PostCard key={post.id || post._id} post={post} searchTerm={search} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
