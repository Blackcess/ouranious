import "./ArticleCommentWrapper.css"
import { postComment,getComments, deleteComment } from "../../APIs/contentDocumentAPI"
import { useEffect, useState } from 'react';
import CommentComposer from "../Comment Composer/CommentComposer";
import CommentList from "../Comment List/CommentList";
import { useAuth } from "../../../../../Recquire Authentication/useAuth";
import { Navigate, useNavigate } from "react-router-dom";
import { FaRegComment } from "react-icons/fa";


export default function ArticleCommentsSection({ contentId,redirect }) {
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const userData = useAuth()
  const navigation= useNavigate()

  // Fetch comments
  useEffect(() => {
    
    async function fetchComments() {
      try {
        const data = await getComments(contentId);
        // console.log("Article Comments are ",data)
        setComments(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
        // console.log("Userdata is ",userData)
      }
    }

    fetchComments();
  }, [contentId]);

  // Create comment 
  async function handleCreate(commentText) {
    if(redirect && redirect.status === true && redirect.from === "article-creation-center"){
      
    }
    if(userData.authenticated === false){
      navigation("/login");
      return;
    }
    setIsSubmitting(true);

    try {
      const data = await postComment(contentId, commentText);

      // optimistic append
      setComments(prev =>{return  [data, ...prev]});

    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  }

  // Delete comment
  async function handleDelete(comment_id) {
    try {
      await deleteComment(comment_id);

      setComments(prev => prev.filter(c => c.comment_id !== comment_id));
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="comments-section">
      <h3 className="comments-title">
        <span className="comment-icon"><FaRegComment /></span>
        <span className="comment-tag">Comments</span>
    </h3>

      <CommentComposer onSubmit={handleCreate} isSubmitting={isSubmitting} />
        <CommentList
            comments={comments}
            isLoading={isLoading}
            onDelete={handleDelete}
        />
    </div>
  );
}
