import { TagModel } from "../Models/tagModel.js";

const TagController = {
  async create(req, res) {
    try {
      const { name } = req.body;
      const tag = await TagModel.create(name);
      res.status(201).json(tag);
    } catch (err) {
      res.status(500).json({ error: 'Failed to create tag' });
    }
  },

  async getAll(req, res) {
    try {
      const tags = await TagModel.findAll();
      res.json(tags);
    } catch (err) {
      res.status(500).json({ error: 'Failed to fetch tags' });
    }
  },

  async getOne(req, res) {
    try {
      const tag = await TagModel.findById(req.params.id);
      if (!tag) return res.status(404).json({ error: 'Tag not found' });
      res.json(tag);
    } catch (err) {
      res.status(500).json({ error: 'Failed to fetch tag' });
    }
  },

  async update(req, res) {
    try {
      const { name } = req.body;
      const tag = await TagModel.update(req.params.id, name);
      res.json(tag);
    } catch (err) {
      res.status(500).json({ error: 'Failed to update tag' });
    }
  },

  async delete(req, res) {
    try {
      await TagModel.remove(req.params.id);
      res.json({ message: 'Tag deleted' });
    } catch (err) {
      res.status(500).json({ error: 'Failed to delete tag' });
    }
  }
};

export {TagController}