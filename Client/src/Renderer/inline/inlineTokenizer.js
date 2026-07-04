export function tokenizeInlineText(text) {
  const regex = /(<\/?[^>]+>)/g;
  return text.split(regex).filter(Boolean);
}
