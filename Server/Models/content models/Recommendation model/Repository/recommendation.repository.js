// recommendation.repository.js
import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";
import { DomainError } from "../../../../Domain Errors/domainErrors.js";

export const RecommendationRepository = {
  /**
   * Article page:
   * More from same category, excluding current article
   * Slight preference for same author (ORDER BY)
   */
  async getRelatedByCategory({
    categoryId,
    authorId,
    excludeContentId,
    limit = 4,
  }) {
    const sql = `
      SELECT
        c.content_id,
        c.title,
        c.slug,
        c.thumbnail_media_id AS thumbnailMediaId,
        c.published_at,
        c.updated_at
      FROM content c
      WHERE
        c.status = 'published'
        AND c.category_id = ?
        AND c.content_id != ?
      ORDER BY
        (c.author_id = ?) DESC,
        c.published_at DESC
      LIMIT ${limit}
    `;

    const [rows] = await connection.execute(sql, [
      categoryId,
      excludeContentId,
      authorId,
    ]);

    return rows;
  },

  /**
   * Category page:
   * Latest articles in a category
   */
  async getByCategory({
    categoryId,
    limit = 20,
  }) {
    const sql = `
      SELECT
        c.content_id,
        c.title,
        c.slug,
        c.thumbnail_media_id AS thumbnailMediaId,
        c.published_at,
        c.updated_at
      FROM content c
      WHERE
        c.status = 'published'
        AND c.category_id = ?
      ORDER BY
        c.published_at DESC
      LIMIT ${limit}
    `;

    const [rows] = await connection.execute(sql, [
      categoryId
    ]);

    return rows;
  },

  /**
   * Author page:
   * Latest articles by an author
   */
  async getByAuthor({
    authorId,
    limit = 10,
  }) {
    const sql = `
      SELECT
        c.content_id,
        c.title,
        c.slug,
        c.thumbnail_media_id AS thumbnailMediaId,
        c.published_at,
        c.updated_at
      FROM content c
      WHERE
        c.status = 'published'
        AND c.author_id = ?
      ORDER BY
        c.published_at DESC
      LIMIT ${limit}
    `;

    const [rows] = await connection.execute(sql, [
      authorId,
    ]);

    return rows;
  },

  /**
   * Home page feed:
   * Latest published articles across categories
   */
  async getHomeFeed({ limit = 10 }) {
  const safeLimit = Number(limit);

  if (!Number.isInteger(safeLimit) || safeLimit <= 0) {
    throw DomainError.invalid("Invalid limit value for getHomeFeed");
  }

  const sql = `
    SELECT
      c.content_id,
      c.title,
      c.slug,
      c.thumbnail_media_id AS thumbnailMediaId,
      c.published_at,
      c.updated_at,
      cat.name AS category_name,
      cat.category_id,
      user.username as author

    FROM content c
    JOIN categories cat ON c.category_id = cat.category_id 
    JOIN users user ON c.author_id = user.id
    WHERE c.status = 'published'
    ORDER BY c.published_at DESC
      LIMIT ${safeLimit}
  `;

  const [rows] = await connection.execute(sql);
  return rows;
}
};