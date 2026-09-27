import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../api/auth'
import toast from 'react-hot-toast'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  const processedRef = useRef(false)

  useEffect(() => {
    if (processedRef.current) return
    processedRef.current = true

    const token = searchParams.get('token')
    const error = searchParams.get('error')

    if (token) {
      localStorage.setItem('token', token)
      authApi.me()
        .then(({ data }) => {
          login(token, data)
          toast.success(`Welcome back, ${data.name || 'friend'}! 🎉`)
          navigate('/', { replace: true })
        })
        .catch((err) => {
          console.error('Failed to fetch user in OAuth callback:', err)
          login(token, null)
          navigate('/', { replace: true })
        })
    } else {
      toast.error(error || 'Authentication failed. Please try again.')
      navigate('/login', { replace: true })
    }
  }, [searchParams, login, navigate])

  return (
    <div className="flex-center" style={{ minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
      <div className="spinner"></div>
      <p className="text-muted">Completing authentication...</p>
    </div>
  )
}
