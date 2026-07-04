import "./CommentList.css"
import CommentItem from "../Comment Item/CommentItem";

export default function CommentList({ comments, isLoading, onDelete }) {
  if (isLoading) return <p>Loading comments...</p>;
  if (!comments.length) return <p className="no-comment">No comments yet.</p>;

  return (
    <ul className="comment-list">
      {comments.map(c => (
        
          
          <CommentItem key={c.comment_id} comment={c} onDelete={onDelete} />
        
        
      ))}
    </ul>
  );
}
