// content.repository.js
import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";

export const ContentRepository = {
  // find by slug
  
  async findBySlug(slug) {
    
    const sql = `
            SELECT c.*,
            a.username AS author_name,
            a.id AS authorId
      FROM content c
      LEFT JOIN users a ON c.author_id = a.id
      WHERE slug = ?
    `;
    const [rows] = await connection.execute(sql, [slug]);
    

    if (rows.length === 0) {
      return null;
    }
    const row = rows[0];
    // console.log("Repository rows is ",row)
    return {
      content_id: row.content_id,
      title: row.title,
      slug: row.slug,
      content_document: row.content_document,
      thumbnailMediaId: row.thumbnail_media_id,
      type: row.type,
      status: row.status,
      updated_at: row.updated_at,
      author_name: row.author_name,
      authorId:row.authorId,
      categoryId: row.category_id,
    };
  },
  async findById(contentId) {
    
    const sql = `
      SELECT c.*,
      a.username AS author_name,
      a.id AS authorId
      FROM content c
      LEFT JOIN users a ON c.author_id = a.id
      WHERE content_id = ?
    `;
    const [rows] = await connection.execute(sql, [contentId]);
    

    if (rows.length === 0) {
      return null;
    }
    const row = rows[0];
    // console.log("Repository rows is ",row)
    return {
      content_id: row.content_id,
      title: row.title,
      slug: row.slug, 
      content_document: row.content_document,
      type: row.type,
      status: row.status,
      updated_at: row.updated_at,
      author_name: row.author_name,
      authorId:row.authorId,
      thumbnailMediaId: row.thumbnail_media_id,
      categoryId: row.category_id,
    };
  },


  
  async upsertDraft({
  contentId,
  authorId,
  title,
  delta,
  type,
  thumbnailMediaId = null,
  categoryId
}) {
  const sql = `
    INSERT INTO content_drafts
  (content_id, author_id, title, delta, type, thumbnail_media_id,category_id)
VALUES (?, ?, ?, ?, ?, ?,?)
ON DUPLICATE KEY UPDATE
  title = VALUES(title),
  delta = VALUES(delta),
  thumbnail_media_id = VALUES(thumbnail_media_id),
  category_id = VALUES(category_id),
  updated_at = CURRENT_TIMESTAMP
  `;

 const params = [
  contentId,
  authorId,
  title,
  JSON.stringify(delta),
  type,
  thumbnailMediaId,
  categoryId
];

  await connection.execute(sql, params);
},

async createDraftContent({
  title,
  slug,
  authorId,
  type,
  categoryId
}) {
  const sql = `
    INSERT INTO content
      (title, slug, content_format, type, status, author_id,category_id)
    VALUES (?, ?, 'blocks_v1', ?, 'draft', ?,?)
  `;

  const [result] = await connection.execute(sql, [
    title,
    slug,
    type,
    authorId,
    categoryId
  ]);

  return result.insertId;
},


async getDraftByContentId({ contentId, authorId }) {
  const sql = `
  SELECT
  content_id,
  title,
  delta,
  type,
  thumbnail_media_id,
  updated_at,
  category_id
FROM content_drafts
WHERE content_id = ? AND author_id = ?
LIMIT 1
  `;

  const [rows] = await connection.execute(sql, [contentId, authorId]);

  if (rows.length === 0) return null;

  return {
    contentId: rows[0].content_id,
    title: rows[0].title,
    delta: rows[0].delta,
    type: rows[0].type,
    thumbnailMediaId: rows[0].thumbnail_media_id,
    updatedAt: rows[0].updated_at,
    categoryId:rows[0].category_id
};
},



async getAllAuthorDrafts(authorId ) {
    const sql = `
      SELECT
        cd.content_id,
        cd.title,
        cd.delta,
        cd.type,
        cd.thumbnail_media_id,
        cd.updated_at,
        cd.category_id,
        u.username AS author_name
      FROM content_drafts cd
      JOIN users u ON cd.author_id = u.id
      WHERE cd.author_id = ?
    `;

  const [rows] = await connection.execute(sql, [authorId]);

  if (rows.length === 0) return null;

  const result = []


  rows.map((row,index)=>{

      const temp =  {
        content_id: rows[0].content_id,
        title: rows[0].title,
        delta: rows[0].delta,
        type: rows[0].type,
        thumbnailMediaId: rows[0].thumbnail_media_id,
        updated_at: rows[0].updated_at,
        categoryId:rows[0].category_id
      };

      result.push(temp)
  })

  return result
},



async getDraftForPublish({ contentId, authorId }) {
  const sql = `
    SELECT title, delta, type, thumbnail_media_id,category_id
    FROM content_drafts
    WHERE content_id = ? AND author_id = ?
    LIMIT 1
  `;

  const [rows] = await connection.execute(sql, [contentId, authorId]);

  if (rows.length === 0) return null;

  return {
    title: rows[0].title,
    delta: rows[0].delta,
    type: rows[0].type,
    thumbnailMediaId: rows[0].thumbnail_media_id,
    categoryId: rows[0].category_id,
  };
},



async publishContent(tc,{
  contentId,
  title,
  blocks,
  thumbnailMediaId = null,
  categoryId
}) {
  const sql = `
    UPDATE content
    SET
      title = ?,
      content_document = ?,
      thumbnail_media_id = ?,
      status = 'published',
      published_at = NOW(),
      category_id=?
    WHERE content_id = ?
  `;

  await tc.execute(sql, [
    title,
    JSON.stringify(blocks),
    thumbnailMediaId,
    categoryId,
    contentId,
  ]);

},



async deleteDraft(tc,{ contentId, authorId }) {
  const sql = `
    DELETE FROM content_drafts
    WHERE content_id = ? AND author_id = ?
  `;

  await tc.execute(sql, [contentId, authorId]);
},


async deleteAuthorDraft(contentId) {   // for now anyone can delete a draft, but in future we will add authorId to this function to make sure only the author can delete their own draft
  const sql = `
    DELETE FROM content_drafts
    WHERE content_id = ?
  `;

  const [affectedRows] = await connection.execute(sql, [contentId]);

  if(affectedRows){
    return true
  }
  return false
},



async deletePublished(id){
  const [affectedRows] = await connection.execute(`
    DELETE FROM content
    WHERE content_id = ?
  `, [id])

  if(affectedRows){
    return true
  }
  return false
},



async getPublishedContents() {
  const sql = `
    SELECT c.*,
    a.username AS author_name
    FROM content c
    LEFT JOIN users a ON c.author_id = a.id
    WHERE status = 'published'
  `;

  const [rows] = await connection.execute(sql);
  // console.log("Come on ",rows)

  return rows.map(row => ({
    content_id: row.content_id,
    title: row.title,
    slug: row.slug,
    content_document: row.content_document,
    type: row.type,
    status: row.status,
    updated_at: row.updated_at,
    author_name: row.author_name,
    thumbnailMediaId: row.thumbnail_media_id,
    categoryId: row.category_id,
  }));
},



async getMyPublishedContent(userId) {
  const sql = `
    SELECT c.*,
    a.username AS author_name
    FROM content c
    LEFT JOIN users a ON c.author_id = a.id
    WHERE status = 'published'
    AND a.id = ?
  `;

  const [rows] = await connection.execute(sql,[userId]);

  return rows.map(row => ({
    content_id: row.content_id,
    title: row.title,
    slug: row.slug,
    content_document: row.content_document,
    type: row.type,
    status: row.status,
    updated_at: row.updated_at,
    author_name: row.author_name,
    thumbnailMediaId: row.thumbnail_media_id,
    categoryId: row.category_id,
  }));
},



async getPublishedContentByCategorySlug(slug){
  const [result] = await connection.query(`
      SELECT
      c.content_id,
      c.title,
      c.slug,
      c.thumbnail_media_id,
      c.updated_at,
      a.username as author_name
    FROM content c
    JOIN users a on a.id = c.author_id
    JOIN categories cat ON c.category_id = cat.category_id
    WHERE
      cat.slug = ?
      AND c.status = 'published'
    ORDER BY c.published_at DESC;
    `,[slug]) 
    if(!result.length){
      return []
    }

    return result.map(result => ({
    content_id: result.content_id,
    title: result.title,
    slug: result.slug,
    content_document: result.content_document,
    type: result.type,
    status: result.status,
    updated_at: result.updated_at,
    author_name: result.author_name,
    thumbnailMediaId: result.thumbnail_media_id,
    categoryId: result.category_id,
  }))
},



};
