import { useState, useCallback, useEffect } from 'react'

export default function SearchBar({ onSearch, placeholder = 'Search posts...', initialValue = '' }) {
  const [value, setValue] = useState(initialValue)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  const handleChange = useCallback((e) => {
    setValue(e.target.value)
    // Debounce: wait 400ms after user stops typing before searching
    clearTimeout(window.__searchTimer)
    window.__searchTimer = setTimeout(() => onSearch?.(e.target.value), 400)
  }, [onSearch])

  return (
    <div className="search-wrapper">
      <span className="search-icon">🔍</span>
      <input
        className="input input--search"
        type="search"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
      />
    </div>
  )
}
