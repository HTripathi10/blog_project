import api from './client'

export const readingHistoryApi = {
  getHistory: (params) => api.get('/reading-history/me', { params }),
  getStats: () => api.get('/reading-history/me/stats'),
  recordReading: (postId) => api.post('/reading-history', null, { params: { post_id: postId } }),
}
