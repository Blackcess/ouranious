import express from "express";
import { CategoryController } from "../Controllers/categoryControllers.js"

const categoryRoute = express.Router()

categoryRoute.post('/', CategoryController.create);
categoryRoute.get('/', CategoryController.getAll);
categoryRoute.get('/:id', CategoryController.getOne);
categoryRoute.put('/:id', CategoryController.update);
categoryRoute.delete('/:id', CategoryController.delete);
categoryRoute.get('/related-content/:id', CategoryController.getRelatedContent);


export {categoryRoute}
