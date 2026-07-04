// contains all mysql queries for content
import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";

const ContentModel ={
    // create content
     async create({ title, slug, body, type, author_id }) {
        const [result] = await connection.query(
                `INSERT INTO content (title, slug, body, type, author_id, status) 
                 VALUES (?, ?, ?, ?, ?, 'draft')`,
                    [title, slug, body, type, author_id]
            );
        return result.insertId;
      },
    //   find content by slug
      async findBySlug(slug) {
        const [rows] = await connection.query(
            `SELECT 
            c.content_id AS article_id,
            c.title,
            c.slug,
            c.body,
            c.type,
            a.name AS author,
            c.status,
            c.published_at, 
            -- Media
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'media_id', m.media_id,
                        'file_path', m.file_path,
                        'attribute', m.attribute,
                        'media_type', m.type,
                        'uploaded_at', m.uploaded_at
                    ) 
                )
                FROM media m
                where m.content_id = c.content_id
            ) AS media,
             
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'tag', t.name,
                'tag_id', t.tag_id
            )
        )
        FROM content_tags ct
        JOIN tags t ON ct.tag_id = t.tag_id
        WHERE ct.content_id = c.content_id
    ) AS tags,
    -- Categories
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'category', cat.name,
                'category_id', cat.category_id
            )
        )
        FROM content_categories_management cm
        JOIN content_categories cat ON cm.category_id = cat.category_id
        WHERE cm.content_id = c.content_id
    ) AS categories

        FROM content c
        JOIN content_users a ON c.author_id = a.user_id
        where c.slug = ?
        ORDER BY c.published_at DESC
        LIMIT 10;`,
            [slug]
        );
        return rows[0];
      },
     
    //   Find all content that is published 
    async findAll() {
       
        try {
          const [rows] = await connection.query(
            `SELECT 
    c.content_id AS article_id,
    c.title,
    c.slug,
    c.body,
    c.type,
    a.name AS author,
    c.status,
    c.published_at,

    -- Media
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'media_id', m.media_id,
                'file_path', m.file_path,
                'attribute', m.attribute,
                'media_type', m.type,
                'uploaded_at', m.uploaded_at
            )
        )
        FROM media m
        WHERE m.content_id = c.content_id
    ) AS media,

    -- Tags
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'tag', t.name,
                'tag_id', t.tag_id
            )
        )
        FROM content_tags ct
        JOIN tags t ON ct.tag_id = t.tag_id
        WHERE ct.content_id = c.content_id
    ) AS tags,

    -- Categories
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'category', cat.name,
                'category_id', cat.category_id
            )
        )
        FROM content_categories_management cm
        JOIN content_categories cat ON cm.category_id = cat.category_id
        WHERE cm.content_id = c.content_id
    ) AS categories

FROM content c
JOIN content_users a ON c.author_id = a.user_id;`
          );
        return rows;
        } catch (error) {
          console.error("Error fetching all content:", error);
        }
    },
    // update the status of content
     async updateStatus(content_id, status) {
        await connection.query(
            'UPDATE content SET status = ?, published_at = NOW() WHERE content_id = ?',
            [status, content_id]
        );
     },
    //  delete content
     async delete(content_id) {
        try {
            await connection.query('DELETE FROM content WHERE content_id = ?', [content_id]);
        } catch (error) {
            console.error("Error deleting content:", error);
        }
     },
    //  attach category to content
    async addCategory(content_id, category_id) {
      await connection.query(
          'INSERT INTO content_categories_management (content_id, category_id) VALUES (?, ?)',
          [content_id, category_id]
      );
    },
    // attach tags
    async addTag(content_id, tag_id) {
      await connection.query(
        'INSERT INTO content_tags (content_id, tag_id) VALUES (?, ?)',
        [content_id, tag_id]
      );
    },
    // find content by category
    async findByCategory(category_id) {
      const [rows] = await connection.query(
        `SELECT c.* FROM content c
          JOIN content_categories_management cm ON c.content_id = cm.content_id
          WHERE cm.category_id = ? AND c.status = 'published'`,
          [category_id]
      );
      return rows;
    },
    // find content by tags
    async findByTag(tag_id) {
      const [rows] = await connection.query(
        `SELECT c.* FROM content c
        JOIN content_tags ct ON c.content_id = ct.content_id
        WHERE ct.tag_id = ? AND c.status = 'published'`,
        [tag_id]
      );
      return rows;
    },
    // find content for card display
    async cardDisplay(id){
      const [rows] = await connection.query(
        `SELECT 
            c.content_id AS article_id,
            c.title,
            c.slug,
            c.body,
            c.type,
            a.name AS author,
            c.status,
            c.published_at, 
            -- Media
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'media_id', m.media_id,
                        'file_path', m.file_path,
                        'attribute', m.attribute,
                        'media_type', m.type,
                        'uploaded_at', m.uploaded_at
                    ) 
                )
                FROM media m
                WHERE m.content_id = c.content_id AND m.attribute = 'thumbNail'
            ) AS media
        FROM content c
        JOIN content_users a ON c.author_id = a.user_id
        where c.content_id = ?
        ORDER BY c.published_at DESC
        LIMIT 10;`,[id]
      );
      console.log("Executed Rows are ",rows)
      return rows;
    }

}

export {ContentModel}