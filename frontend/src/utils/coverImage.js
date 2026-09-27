export function getCoverImage(post) {
  return post?.cover_image_url || null
}

export function coverFallbackTone(post) {
  const seed = Number(post?.id || post?.post_id || 0)
  return Math.abs(seed) % 5
}

export function coverLetter(post) {
  const title = (post?.title || post?.post_title || 'P').trim()
  return (title[0] || 'P').toUpperCase()
}
