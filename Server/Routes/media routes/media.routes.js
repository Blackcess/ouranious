import express from "express";
import multer from "multer";
import { 
    uploadImageController,
    addExternalVideoController,
    listMediaController
 } from "../../Controllers/media controllers/media.controller.js";
 import { authenticationMiddleware } from "../../Middlewares/authenticationMiddleware.js";
 import { mediaImageUpload } from "../../Middlewares/Media For Content documents uploads/mediaUpload.multer.js";


//  This Router layer is minimum viable-=> It recquires some thitches
const mediaRouter = express.Router();

mediaRouter.use(authenticationMiddleware)

mediaRouter.post(
  "/upload",
  mediaImageUpload.single("image"),
  uploadImageController
);

mediaRouter.post(
  "/external",
  addExternalVideoController
);

mediaRouter.get(
  "/",
  listMediaController
);

export default mediaRouter;