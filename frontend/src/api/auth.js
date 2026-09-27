import api from './client'

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  googleLogin: () => {
    const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const next = encodeURIComponent(window.location.origin)
    window.location.href = `${backendUrl}/api/auth/google?next=${next}`
  },
}
