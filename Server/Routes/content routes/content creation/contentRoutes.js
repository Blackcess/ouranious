import { ContentController } from "../../../Controllers/content controllers/contentControllers.js";
import express from "express";
import { authenticationMiddleware } from "../../../Middlewares/authenticationMiddleware.js";
import { getRecommendations } from "../../../Controllers/content controllers/recommendation controllers/content.recommendation.controller.js";
import { createCommentController,getCommentsController,deleteCommentController } from "../../../Controllers/content controllers/content interactions controllers/content comments controllers/contentCommentsControllers.js";
import { isAdminMiddleware } from "../../../Middlewares/isAdminMiddleware.js";
const contentRouter = express.Router();


// CRUD routes
contentRouter.get("/recommendations",getRecommendations)
contentRouter.post('/draft', authenticationMiddleware,ContentController.saveDraftController);        // Create new article/blog
contentRouter.get('/draft/:contentId', authenticationMiddleware, ContentController.loadDraftController);    // Load draft
contentRouter.get('/all/drafts', authenticationMiddleware, ContentController.loadAuthorDraftController);    // Load All Authors' draft
contentRouter.post('/:contentId/publish', authenticationMiddleware, ContentController.publishContentController);    // Load draft
contentRouter.get('/:slug', ContentController.getBySlug);    // Get single by slug
contentRouter.get('/:contentId', ContentController.getById);    // Get single by contentId
contentRouter.get('/all/published', ContentController.getPublishedContentsController);    // Get all published contents
contentRouter.get('/all/my-published', authenticationMiddleware,ContentController.getMyPublishedContentsController);    // Get all authors' published contents 
contentRouter.get('/category/slug/:slug/published', ContentController.getPublishedContentByCategorySlugController);    // Get all published contents by category slug
contentRouter.post("/media/resolve",ContentController.resolveMediaController)
contentRouter.get("/media/:id",ContentController.getMediaByIdController)
contentRouter.post("/comment",authenticationMiddleware,createCommentController)
contentRouter.get("/:content_id/comments",getCommentsController)
contentRouter.delete("/comment/:comment_id",authenticationMiddleware,deleteCommentController)
contentRouter.delete(`/published`, authenticationMiddleware, ContentController.deletePublishedController)
contentRouter.delete(`/draft`, authenticationMiddleware, ContentController.deleteDraftController)


export {contentRouter}