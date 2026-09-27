import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer__inner">
        <div>
          <Link to="/" className="navbar__logo site-footer__logo">Perspective</Link>
          <p className="site-footer__tagline">A feed for ideas that move — essays, notes, and experiments.</p>
        </div>
        <p className="site-footer__copy">© {new Date().getFullYear()} Perspective</p>
      </div>
    </footer>
  )
}
