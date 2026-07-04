import "./CommentComposer.css"

import { useState } from 'react';

export default function CommentComposer({ onSubmit, isSubmitting }) {
  const [text, setText] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;

    onSubmit(text);
    setText('');
  }

  return (
    <form className="comment-composer" onSubmit={handleSubmit}>
      <textarea
        placeholder="Write a comment..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button disabled={isSubmitting}>
        {isSubmitting ? 'Posting...' : 'Post Comment'}
      </button>
    </form>
  );
}
