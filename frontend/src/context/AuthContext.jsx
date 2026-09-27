/**
 * context/AuthContext.jsx — Global authentication state
 *
 * 💡 CONCEPT: React Context
 *    Context lets us share state (like "who is logged in") across the entire
 *    component tree without passing props through every level (prop drilling).
 *
 *    Pattern:
 *    1. Create context with createContext()
 *    2. Wrap your app in <AuthProvider> — this holds the state
 *    3. Any component can call useAuth() to read/update that state
 *
 * 💡 CONCEPT: Token Storage Strategy
 *    We store the JWT in localStorage for simplicity. In a high-security app
 *    you'd use httpOnly cookies (not accessible from JS = XSS-safe).
 *    localStorage is fine for this bootcamp project.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    // Initialize from localStorage so page refresh doesn't log user out
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  // Verify token on first load (token might be expired)
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }
    authApi.me()
      .then(({ data }) => setUser(data))
      .catch(() => logout())          // Token invalid → clear everything
      .finally(() => setLoading(false))
  }, [])

  // Listen for auto-logout events from axios interceptor
  useEffect(() => {
    const handler = () => logout()
    window.addEventListener('auth:logout', handler)
    return () => window.removeEventListener('auth:logout', handler)
  }, [])

  const login = useCallback((token, userData) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  const updateUser = useCallback((updatedUser) => {
    localStorage.setItem('user', JSON.stringify(updatedUser))
    setUser(updatedUser)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateUser, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
