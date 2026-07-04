import { useEffect } from "react";
import "./CommentItem.css"

export default function CommentItem({ comment, onDelete }) {
    
  return (
    <div className="comment-display">
      <span className="comment-dash">-</span>
      <li className="comment-item">
      <div className="comment-header">
        <span className="user-image"></span>
        <span className="comment-user">{comment.username}</span>
        
      </div>
      <span className="comment-date">
          {new Date(comment.created_at).toLocaleString()}
        </span>

      <p className="comment-text">{comment.comment}</p>

      {comment.can_delete && (
        <button
          className="comment-delete"
          onClick={() => onDelete(comment.comment_id)}
        >
          Delete
        </button>
      )}
      </li>
    </div>
    
  );
}
