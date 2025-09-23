import { TagController } from "../Controllers/tagController.js";
import express from "express";

const tagRouter = express.Router()

tagRouter.post('/', TagController.create);
tagRouter.get('/', TagController.getAll);
tagRouter.get('/:id', TagController.getOne);
tagRouter.put('/:id', TagController.update);
tagRouter.delete('/:id', TagController.delete);

export {tagRouter}

