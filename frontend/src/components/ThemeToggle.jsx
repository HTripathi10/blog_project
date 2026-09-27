import { useTheme } from '../context/ThemeContext'

export default function ThemeToggle() {
  const { toggleTheme, isDark } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      title={isDark ? 'Switch to Light mode' : 'Switch to Dark mode'}
      aria-label="Toggle theme"
      type="button"
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  )
}
