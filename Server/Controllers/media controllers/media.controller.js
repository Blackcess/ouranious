import { uploadImage } from "../../Models/media models/services/uploadImage.service.js";
import { addExternalVideo } from "../../Models/media models/services/addExternalVideo.service.js";
import { listMediaByUser } from "../../Models/media models/repository/media.repository.js";

export async function uploadImageController(req, res, next) {
  try {
    const authorId = req.user.id;
    const result = await uploadImage({
      file: req.file,
      authorId,
    });

    res.status(201).json({ data: result });
  } catch (err) {
    next(err);
  }
}

export async function addExternalVideoController(req, res, next) {
  try {
    const authorId = req.user.id;
    const { url } = req.body;

    const result = await addExternalVideo({
      url,
      authorId,
    });

    res.status(201).json({ data: result });
  } catch (err) {
    next(err);
  }
}

export async function listMediaController(req, res, next) {
  try {
    const userId = req.user.id;
    const media = await listMediaByUser({ userId });

    res.status(200).json({ data: media });
  } catch (err) {
    next(err);
  }
}
