import { connection } from "../Database Module/Database Connection/databaseConnect.js";

const CommentModel = {
    async create(content_id, user_id, comment) {
        const [result] = await db.query(
            'INSERT INTO comments (content_id, user_id, comment) VALUES (?, ?, ?)',
            [content_id, user_id, comment]
        );
        return {
            comment_id: result.insertId,
            content_id,
            user_id,
            comment
        };
    },

    async findByContent(content_id) {
        const [rows] = await db.query(
            `SELECT c.comment_id, c.comment, c.created_at, 
            u.user_id, u.name AS user_name
            FROM comments c
            JOIN content_users u ON c.user_id = u.user_id
            WHERE c.content_id = ?
            ORDER BY c.created_at DESC`,
        [content_id]
        );
        return rows;
     },

  async findById(comment_id) {
    const [rows] = await db.query(
      'SELECT * FROM comments WHERE comment_id = ?',
      [comment_id]
    );
    return rows[0];
  },

  async update(comment_id, comment) {
    await db.query(
      'UPDATE comments SET comment = ? WHERE comment_id = ?',
      [comment, comment_id]
    );
    return { comment_id, comment };
  },

  async remove(comment_id) {
    await db.query('DELETE FROM comments WHERE comment_id = ?', [comment_id]);
  }
};

export {CommentModel}