import { connection } from "../Database Module/Database Connection/databaseConnect.js";

const CategoryModel = {
  async create(name) {
    const [result] = await connection.query(
      'INSERT INTO content_categories (name) VALUES (?)',
      [name]
    );
    return { category_id: result.insertId, name};
  },

  async findAll() {
    const [rows] = await connection.query('SELECT * FROM content_categories');
    return rows;
  },

  async findById(id) {
    const [rows] = await connection.query(
      'SELECT * FROM content_categories WHERE category_id = ?',
      [id]
    );
    return rows[0];
  },

  async update(id, name, description) {
    await connection.query(
      'UPDATE content_categories SET name = ? WHERE category_id = ?',
      [name, id]
    );
    return { category_id: id, name};
  },

  async remove(id) {
    await connection.query('DELETE FROM content_categories WHERE category_id = ?', [id]);
  },
  // intersting content operations
  async getRelatedContent(categoryId) {
    const [rows] = await connection.query(
      `SELECT c.content_id FROM content c
       JOIN content_categories_management ac ON c.content_id = ac.content_id
       WHERE ac.category_id = ?`,
      [categoryId]
    );
    return rows;
  }
};

export {CategoryModel}