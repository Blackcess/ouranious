import { connection } from "../../../Database Module/Database Connection/databaseConnect.js";

export async function createMedia({
  type,
  source,
  url,
  thumbnailUrl = null,
  width = null,
  height = null,
  createdBy,
}) {
  const sql = `
    INSERT INTO media
      (type, source, url, thumbnail_url, width, height, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `;

  const [result] = await connection.execute(sql, [
    type,
    source,
    url,
    thumbnailUrl,
    width,
    height,
    createdBy,
  ]);

  return result.insertId;
}

export async function listMediaByUser({ userId }) {
  const sql = `
    SELECT media_id, type, source, url, thumbnail_url, width, height
    FROM media
    WHERE created_by = ? AND status = 'active'
    ORDER BY created_at DESC
  `;

  const [rows] = await connection.execute(sql, [userId]);
  return rows;
}

export async function getMediaById(mediaId) {
  const sql = `
    SELECT media_id, type, source, url, thumbnail_url, width, height, status
    FROM media
    WHERE media_id = ?
    LIMIT 1
  `;

  const [rows] = await connection.execute(sql, [mediaId]);
  return rows.length ? rows[0] : null;
}

export async function getMediaByIds(mediaIds = []) {
  if (!Array.isArray(mediaIds) || mediaIds.length === 0) {
    return [];
  }
  
  const placeholders = mediaIds.map(() => "?").join(",");

  const sql = `
    SELECT 
      media_id,
      type,
      source,
      url,
      thumbnail_url,
      width,
      height
    FROM media
    WHERE media_id IN (${placeholders})
      AND status = 'active'
  `;

  const [rows] = await connection.execute(sql, mediaIds);
  return rows; 
}