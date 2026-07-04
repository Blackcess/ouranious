import { createMedia } from "../repository/media.repository.js";
import path from "path";
import fs from "fs";
import { DomainError } from "../../../Domain Errors/domainErrors.js";

export async function uploadImage({
  file,
  authorId,
}) {
  if (!file) {
    throw DomainError.invalid("NO_FILE_UPLOADED")
  }

  if (!file.mimetype.startsWith("image/")) {
    throw DomainError.invalid("INVALID_IMAGE_TYPE");
  }
  const UPLOADS_ROOT = path.resolve("uploads");

  // Assume file already stored by multer
  // const url = `/uploads/images/${file.filename}`;   
  const relativePath = path.relative(UPLOADS_ROOT, file.path);
  const normalizedPath = relativePath.replace(/\\/g, "/");
  const url = `/uploads/${normalizedPath}`;

  const mediaId = await createMedia({
    type: "image",
    source: "upload",
    url,
    createdBy: authorId,
  });

  return {
    media_id:mediaId,
    url,
  };
}
