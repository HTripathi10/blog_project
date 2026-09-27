/** Renders a coloured circle with initials when no avatar image is available */
export default function AvatarPlaceholder({ name = '?', size = 'md' }) {
  const initial = name.charAt(0).toUpperCase()
  // Generate a consistent colour from the name
  const colors = ['#7c6af7', '#63b3ed', '#68d391', '#fc8181', '#f6ad55', '#b794f4']
  const idx = name.charCodeAt(0) % colors.length
  return (
    <div
      className={`avatar avatar--${size}`}
      style={{ background: colors[idx], color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}
    >
      {initial}
    </div>
  )
}
