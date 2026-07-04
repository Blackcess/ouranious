// category.routes.js
import express from "express";
import { CategoryController } from "../../Controllers/category controller/category.controller.js";

const categoryRouter = express.Router();

/**
 * GET /categories
 * List all categories
 */
categoryRouter.get("/", CategoryController.listAllCategories);

/**
 * GET /categories/id/:categoryId
 * Get category by ID
 */
categoryRouter.get("/id/:categoryId", CategoryController.getCategoryById);

/**
 * GET /categories/slug/:slug
 * Get category by slug
 */
categoryRouter.get("/slug/:slug", CategoryController.getCategoryBySlug);

export default categoryRouter;