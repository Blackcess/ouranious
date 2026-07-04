import { DomainError } from "../../../../../Domain Errors/domainErrors.js";
import { connection } from "../../../../../Database Module/Database Connection/databaseConnect.js";


async function createComment({ content_id, user_id, comment }) {
  const sql = `
    INSERT INTO comments (content_id, commenter_id, comment)
    VALUES (?, ?, ?)
  `;
  const [result] = await connection.execute(sql, [content_id, user_id, comment]);
  if(result.affectedRows === 0){
    throw DomainError.invalid("Failed to create comment");  
  }
  const [[{created_at, username}]] = await connection.execute(`
    SELECT c.created_at,
    u.username
    FROM comments c
    JOIN users u ON c.commenter_id = u.id
    WHERE c.comment_id = ?`
    , [result.insertId]);
  return {
    comment_id: result.insertId,
    content_id,
    user_id:result.commenter_id,
    comment,
    created_at:created_at,
    username
  };
}

async function getCommentsByContentId(content_id) {
  const sql = `
    SELECT c.comment_id, c.comment, c.created_at,
           u.id, u.username
    FROM comments c
    JOIN users u ON c.commenter_id = u.id
    WHERE c.content_id = ?
    ORDER BY c.created_at DESC
  `;
  const [rows] = await connection.execute(sql, [content_id]);
  return rows;
}

async function getCommentById(comment_id) {
  const sql = `SELECT * FROM comments WHERE comment_id = ?`;
  const [rows] = await connection.execute(sql, [comment_id]);
  return rows[0] || null;
}

async function deleteComment(comment_id) {
  const sql = `DELETE FROM comments WHERE comment_id = ?`;
  const [result] = await connection.execute(sql, [comment_id]);
  return result.affectedRows > 0;
}

export {
  createComment,
  getCommentsByContentId,
  getCommentById,
  deleteComment,
};
