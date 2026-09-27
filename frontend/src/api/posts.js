import api from './client'

export const postsApi = {
  // Public
  list: (params) => api.get('/posts', { params }),       // { page, limit, search, tag }
  get: (id) => api.get(`/posts/${id}`),

  // Authenticated
  create: (data) => api.post('/posts', data),
  update: (id, data) => api.put(`/posts/${id}`, data),
  delete: (id) => api.delete(`/posts/${id}`),
  togglePublish: (id) => api.patch(`/posts/${id}/publish`),
  toggleLike: (id) => api.post(`/posts/${id}/like`),
  uploadCover: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/posts/cover-image', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Comments
  listComments: (postId) => api.get(`/posts/${postId}/comments`),
  addComment: (postId, data) => api.post(`/posts/${postId}/comments`, data),
  updateComment: (postId, commentId, data) => api.put(`/posts/${postId}/comments/${commentId}`, data),
  deleteComment: (postId, commentId) => api.delete(`/posts/${postId}/comments/${commentId}`),
}
