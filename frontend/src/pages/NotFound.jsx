import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="empty-state not-found">
      <p className="hero__eyebrow">Lost page</p>
      <h1 className="not-found__code">404</h1>
      <h2 className="empty-state__title">This page is off the map.</h2>
      <p className="empty-state__text">
        The page you are looking for might have been removed, or the address is incomplete.
      </p>
      <Link to="/" className="btn btn-primary">
        Back to home
      </Link>
    </div>
  )
}
