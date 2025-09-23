import e from "express";
import { CommentController } from "../Controllers/commentController.js";

const commentRouter = e.Router();

// Add a comment
commentRouter.post('/', CommentController.create);
// Get all comments for a specific content item
commentRouter.get('/content/:content_id', CommentController.getByContent);
// Update a comment
commentRouter.put('/:id', CommentController.update);
// Delete a comment
commentRouter.delete('/:id', CommentController.delete);

export {commentRouter}