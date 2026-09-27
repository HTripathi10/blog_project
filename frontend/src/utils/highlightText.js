/**
 * Highlights search terms in text by wrapping them in a span with a highlight class
 * @param {string} text - The text to highlight
 * @param {string} searchTerm - The search term to highlight
 * @returns {string} - HTML string with highlighted terms
 */
export function highlightText(text, searchTerm) {
  if (!text || !searchTerm) return text

  const regex = new RegExp(`(${escapeRegex(searchTerm)})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * Escapes special regex characters in a string
 * @param {string} string - The string to escape
 * @returns {string} - The escaped string
 */
function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
