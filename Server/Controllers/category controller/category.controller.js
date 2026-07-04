// category.controller.js
import { CategoryService } from "../../Models/category models/service/category.service.js";

export const CategoryController = {
  async listAllCategories(req, res, next) {
    try {
      const categories = await CategoryService.listAllCategories();
      res.status(200).json({data:categories});
    } catch (err) {
      next(err);
    }
  },

  async getCategoryById(req, res, next) {
    try {
      const categoryId = Number(req.params.categoryId);
      const category = await CategoryService.getCategoryById(categoryId);
      res.status(200).json({data:category});
    } catch (err) {
      next(err);
    }
  },

  async getCategoryBySlug(req, res, next) {
    try {
      const { slug } = req.params;
      const category = await CategoryService.getCategoryBySlug(slug);
      res.status(200).json({data:category});
    } catch (err) {
      next(err);
    }
  },
};