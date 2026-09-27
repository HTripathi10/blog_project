/**
 * api/client.js — Axios instance with automatic JWT injection
 *
 * 💡 CONCEPT: API Client Abstraction
 *    Instead of writing fetch() with headers in every component,
 *    we configure a shared axios instance once. It:
 *    - Automatically adds the Authorization header from localStorage
 *    - Handles 401 responses by clearing the stored token
 *    - Sets the base URL so components just call api.get('/posts')
 */

import axios from 'axios'

const api = axios.create({
  baseURL: '/api',  // Vite proxy forwards this to http://localhost:8000/api
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — add JWT to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor — auto logout on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Optionally redirect to login — we'll let AuthContext handle this
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  }
)

export default api
