// utils/slugify.js
function slugify(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')   // remove invalid chars
    .replace(/\s+/g, '-')           // spaces → hyphens
    .replace(/-+/g, '-');           // collapse multiple hyphens
}

export {slugify}