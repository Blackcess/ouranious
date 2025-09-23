import { PostAllController } from "../Controllers/postAllController.js";
import e from "express"

const postAllRouter = e.Router();

postAllRouter.post("/",PostAllController.post)

export {postAllRouter}