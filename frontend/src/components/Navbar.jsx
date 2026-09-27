import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import SearchBar from './SearchBar'
import AvatarPlaceholder from './AvatarPlaceholder'
import ThemeToggle from './ThemeToggle'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleSearch = (query) => {
    // Check if we're on a profile page
    const profileMatch = location.pathname.match(/^\/profile\/(\d+)$/)
    if (profileMatch) {
      const userId = profileMatch[1]
      if (query) {
        navigate(`/profile/${userId}?search=${encodeURIComponent(query)}`)
      } else {
        navigate(`/profile/${userId}`)
      }
    } else {
      // Default to home page search
      if (query) {
        navigate(`/?search=${encodeURIComponent(query)}`)
      } else {
        navigate('/')
      }
    }
  }

  return (
    <nav className="navbar">
      <div className="navbar__inner">
        <Link to="/" className="navbar__logo">
          <span className="navbar__mark" aria-hidden="true">P</span>
          Perspective
        </Link>

        <div className="navbar__search">
          <SearchBar onSearch={handleSearch} placeholder="Search articles..." />
        </div>

        <div className="navbar__actions">
          <ThemeToggle />
          {isAuthenticated ? (
            <>
              <Link to="/reading-history" className="btn btn--ghost btn--sm" title="Reading History">📖</Link>
              <Link to="/create" className="btn btn--primary btn--sm">+ New Post</Link>
              <Link to={`/profile/${user?.id || user?._id || ''}`} className="btn btn--icon" title={user?.name}>
                {user?.avatar_url
                  ? <img src={user.avatar_url} alt={user.name} className="avatar avatar--sm" />
                  : <AvatarPlaceholder name={user?.name || user?.email} size="sm" />
                }
              </Link>
              <button onClick={handleLogout} className="btn btn--ghost btn--sm">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--ghost btn--sm">Login</Link>
              <Link to="/register" className="btn btn--primary btn--sm">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
