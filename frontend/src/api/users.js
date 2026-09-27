import api from './client'

export const usersApi = {
  getProfile: (userId) => api.get(`/users/${userId}/profile`),
  updateProfile: (data) => api.put('/users/me', data),
  uploadAvatar: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/users/me/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  removeAvatar: () => api.delete('/users/me/avatar'),
  getPosts: (params) => api.get('/users/me/posts', { params }),
}
