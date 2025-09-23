import { ContentController } from "../Controllers/contentControllers.js";
import express from "express";

const contentRouter = express.Router();
// CRUD routes
contentRouter.post('/', ContentController.create);        // Create new article/blog
contentRouter.get('/', ContentController.getAll);         // List all published content
contentRouter.get('/:slug', ContentController.getOne);    // Get single by slug
contentRouter.put('/:id/publish', ContentController.publish); // Publish article
contentRouter.delete('/:id', ContentController.delete);   // Delete article
contentRouter.post('/assign-category', ContentController.assignCategory); //assign category to content
contentRouter.post('/assign-tag', ContentController.assignTag); //assign tags to content
contentRouter.get('/category/:category_id', ContentController.getByCategory); // get content by category
contentRouter.get('/tag/:tag_id', ContentController.getByTag);  //get content by tag
contentRouter.get('/card/display/:id', ContentController.getCardData); // get content for card display

export {contentRouter}