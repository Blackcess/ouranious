import { createCommentService,getCommentsForContentService,deleteCommentService } from "../../../../Models/content models/content interaction models/content comments models/content comments service/contentCommentsService.js";

async function createCommentController(req, res, next) {
  try {
    const { content_id, comment } = req.body;
    const user_id = req.user.id; // from auth middleware

    const result = await createCommentService({
      content_id,
      user_id,
      comment,
    });

    res.status(201).json({
      success: true,
      data: result,
    });
  } catch (err) {
    next(err);
  }
}

async function getCommentsController(req, res, next) {
  try {
    const content_id = parseInt(req.params.content_id);

    const comments = await getCommentsForContentService(content_id);

    res.json({
      success: true,
      data: comments,
    });
  } catch (err) {
    next(err);
  }
}

async function deleteCommentController(req, res, next) {
  try {
    const comment_id = parseInt(req.params.comment_id);

    await deleteCommentService({
      comment_id,
      requester_id: req.user.id,
    });

    res.json({
      success: true,
      message: 'Comment deleted',
    });
  } catch (err) {
    next(err);
  }
}

export{
  createCommentController,
  getCommentsController,
  deleteCommentController,
};
