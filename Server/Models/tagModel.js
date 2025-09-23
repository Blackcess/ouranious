import { connection } from "../Database Module/Database Connection/databaseConnect.js";

const TagModel = {
  async create(name) {
    const [result] = await connection.query(
      'INSERT INTO tags (name) VALUES (?)',
      [name]
    );
    return { tag_id: result.insertId, name };
  },

  async findAll() {
    const [rows] = await connection.query('SELECT * FROM tags');
    return rows;
  },

  async findById(id) {
    const [rows] = await connection.query('SELECT * FROM tags WHERE tag_id = ?', [id]);
    return rows[0];
  },

  async update(id, name) {
    await connection.query('UPDATE tags SET name = ? WHERE tag_id = ?', [name, id]);
    return { tag_id: id, name };
  },

  async remove(id) {
    await connection.query('DELETE FROM tags WHERE tag_id = ?', [id]);
  }
};

export {TagModel}