import { coverFallbackTone, coverLetter, getCoverImage } from '../utils/coverImage'

export default function CoverVisual({ post, className = '' }) {
  const cover = getCoverImage(post)
  if (cover) {
    return <img className={className} src={cover} alt="" />
  }

  return (
    <div
      className={`cover-fallback cover-fallback--${coverFallbackTone(post)} ${className}`}
      aria-hidden="true"
    >
      <span className="cover-fallback__mark">{coverLetter(post)}</span>
    </div>
  )
}
