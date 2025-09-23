import { CategoryModel } from "../Models/categoryModel.js";

const CategoryController = {
  async create(req, res) {
    try {
      const { name } = req.body;
      const category = await CategoryModel.create(name);
      res.status(201).json(category);
    } catch (err) {
      res.status(500).json({ error: 'Failed to create category' });
    }
  },

  async getAll(req, res) {
    try {
      const categories = await CategoryModel.findAll();
      res.json({data:categories, status:true});
    } catch (err) {
      res.status(500).json({ error: 'Failed to fetch categories' , status:false});
    }
  },

  async getOne(req, res) {
    try {
      const category = await CategoryModel.findById(req.params.id);
      if (!category) return res.status(404).json({ error: 'Category not found' });
      res.json(category);
    } catch (err) {
      res.status(500).json({ error: 'Failed to fetch category' });
    }
  },

  async update(req, res) {
    try {
      const { name, description } = req.body;
      const category = await CategoryModel.update(req.params.id, name, description);
      res.json(category);
    } catch (err) {
      res.status(500).json({ error: 'Failed to update category' });
    }
  },

  async delete(req, res) {
    try {
      await CategoryModel.remove(req.params.id);
      res.json({ message: 'Category deleted' });
    } catch (err) {
      res.status(500).json({ error: 'Failed to delete category' });
    }
  },
 async getRelatedContent(req, res) {
    try { 
      const categoryId = req.params.id;
      const content = await CategoryModel.getRelatedContent(categoryId);
      res.json({data:content, status:true});
    } catch (err) {
      console.error(err)
      res.status(500).json({ error: 'Failed to fetch related content' , status:false});
    }
  }
};

export {CategoryController}