import multer from "multer";
import fs from "fs";
import path from "path";

/**
 * Base upload directory (DO NOT change lightly)
 */
const BASE_UPLOAD_DIR = path.resolve("uploads/media");

/**
 * Ensure directory exists
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Storage engine
 */
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const authorId = process.env.DEV_MODE_AUTHOR_ID;

    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");

    const uploadDir = path.join(
      BASE_UPLOAD_DIR,
      "images",
      `user_${authorId}`,
      `${year}`,
      `${month}`
    );

    ensureDir(uploadDir);
    cb(null, uploadDir);
  },

  filename: function (req, file, cb) {
    const ext = path.extname(file.originalname);
    const unique =
      Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);

    cb(null, `${unique}${ext}`);
  },
});

/**
 * File filter
 */
function imageFileFilter(req, file, cb) {
  const allowed = ["image/jpeg", "image/png", "image/webp"];

  if (!allowed.includes(file.mimetype)) {
    cb(new Error("Unsupported image type"), false);
  } else {
    cb(null, true);
  }
}

/**
 * Exported multer instance
 */
export const mediaImageUpload = multer({
  storage,
  fileFilter: imageFileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
  },
});
