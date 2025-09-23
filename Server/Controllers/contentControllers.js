// This is were we use the slugify utility
import { connection } from "../Database Module/Database Connection/databaseConnect.js";
import { ContentModel } from "../Models/contentModels.js";
import { slugify } from "../src/utils/slugify.js";


const ContentController = {
    // creation controller
    async create(req, res) {
        try {
            const { title, body, type, author_id } = req.body;

            // generate slug
            let slug = slugify(title);

            // ensure uniqueness (basic check)
            let existing = await ContentModel.findBySlug(slug);
            if (existing) slug = `${slug}-${Date.now()}`;

            const id = await ContentModel.create({ title, slug, body, type, author_id });

            res.status(201).json({ message: 'Content created', id, slug });
        } catch (err) {
            console.error(err);
            res.status(500).json({ error: 'Failed to create content' });
        }
    },
    // Get all published content controller
    async getAll(req, res) {
        try {
            const content = await ContentModel.findAll();
            res.status(200).json({status:true,data:content});
        } catch (err) {
            res.status(500).json({ error: 'Failed to fetch content' });
        }
    },
    // Retrieve content by a slug
    async getOne(req, res) {
        try {
            const { slug } = req.params;
            console.log("My backend slug is ",slug)
            const content = await ContentModel.findBySlug(slug);
            if (!content) return res.status(404).json({ error: 'Not found' });
            res.status(200).json({data:content,status:true});
        } catch (err) {
            console.error(err)
            res.status(500).json({ error: 'Failed to fetch content',status:false });
        }
    },
    //   Publish Content
    async publish(req, res) {
        try {
            const { id } = req.params;
            const [row]=await ContentModel.updateStatus(id, 'published');
            console.log("row",row)
            res.status(200).json({ message: 'Content published' });
        } catch (err) {
            res.status(500).json({ error: 'Failed to update status' });
        }
    },   

    // delete content controller
    async delete(req, res) {
        try {
            const { id } = req.params;
            await ContentModel.delete(id);
            res.status(200).json({ message: 'Content deleted' });
        } catch (err) {
            res.status(500).json({ error: 'Failed to delete content' });
        }
    },
    // assign category and tags to content
    async assignCategory(req, res) {
        try {
            const { content_id, category_id } = req.body;
            await ContentModel.addCategory(content_id, category_id);
            res.json({ message: 'Category assigned' });
        } catch (err) {
            res.status(500).json({ error: 'Failed to assign category' });
    }
  },
  async assignTag(req, res) {
    try {
      const { content_id, tag_id } = req.body;
      await ContentModel.addTag(content_id, tag_id);
      res.json({ message: 'Tag assigned' });
    } catch (err) {
      res.status(500).json({ error: 'Failed to assign tag' });
    }
  },
//   search by category and tags
    async getByCategory(req, res) {
        try {
            const { category_id } = req.params;
            const content = await ContentModel.findByCategory(category_id);
            res.json(content);
        } catch (err) {
            res.status(500).json({ error: 'Failed to fetch content by category' });
        }
    },

    async getByTag(req, res) {
        try {
            const { tag_id } = req.params;
            const content = await ContentModel.findByTag(tag_id);
            res.json(content);
        } catch (err) {
            res.status(500).json({ error: 'Failed to fetch content by tag' });
        }
  },

//   get data for card display
    async getCardData(req,res){
        try {
            const content_id = req.params.id;
            const content = await ContentModel.cardDisplay(parseInt(content_id));
            res.status(200).json({status:true,data:content})
        } catch (error) {
            console.error(error)
            res.status(500).json({ error: 'Failed to fetch content card data' });
        }
    }


}
export {ContentController}