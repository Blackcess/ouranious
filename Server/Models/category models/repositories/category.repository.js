import { connection } from "../../../Database Module/Database Connection/databaseConnect.js";

export const CategoryRepository = {
  async listAllCategories() {
    const sql = `
      SELECT
        category_id,
        name,
        slug,
        description
      FROM categories
      ORDER BY name ASC
    `;

    const [rows] = await connection.execute(sql);

    return rows.map(row => ({
      categoryId: row.category_id,
      name: row.name,
      slug: row.slug,
      description: row.description,
    }));
  },

  async getCategoryById(categoryId) {
    const sql = `
      SELECT
        category_id,
        name,
        slug,
        description
      FROM categories
      WHERE category_id = ?
      LIMIT 1
    `;

    const [rows] = await connection.execute(sql, [categoryId]);

    if (rows.length === 0) return null;

    const row = rows[0];

    return {
      categoryId: row.category_id,
      name: row.name,
      slug: row.slug,
      description: row.description,
    };
  },

  async getCategoryBySlug(slug) {
    const sql = `
      SELECT
        category_id,
        name,
        slug,
        description
      FROM categories
      WHERE slug = ?
      LIMIT 1
    `;

    const [rows] = await connection.execute(sql, [slug]);

    if (rows.length === 0) return null;

    const row = rows[0];

    return {
      categoryId: row.category_id,
      name: row.name,
      slug: row.slug,
      description: row.description,
    };
  },
};

