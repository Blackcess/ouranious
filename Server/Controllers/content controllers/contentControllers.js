// This is were we use the slugify utility
import { connection } from "../../Database Module/Database Connection/databaseConnect.js";
import { DomainError } from "../../Domain Errors/domainErrors.js";
import { getContentBySlug,
        saveDraft,loadDraft,
        getContentById,
        publishContentService, 
        getPublishedContents, 
        getMediaByIdService, 
        getPublishedByCategorySlug, 
        getMyPublishedContent, 
        deletePublishedService, 
        loadAuthorDrafts,
        deleteAuthorDraftService,
    } 
from "../../Models/content models/content creation models/services/content.service.js";
import { resolveMedia } from "../../Models/content models/content creation models/services/content.service.js";

const ContentController = {
    // Retrieve content by a slug
    async getBySlug(req, res) {
            const { slug } = req.params;
            // console.log("The param is ",slug)
            const content = await getContentBySlug(slug);
            res.status(200).json({ data: content, status: true });
    },
    async getById(req, res) {
            const { contentId } = req.params;
            // console.log("The param is ",contentId)
            const content = await getContentById(Number(contentId));
            res.status(200).json({ data: content, status: true });
    },

    async saveDraftController(req, res) {
        const { contentId, title, delta, type,thumbnailMediaId,categoryId } = req.body;
        const authorId = req.user.id; // from session middleware
        // console.log("Author id is ",authorId)

        if (!title || !delta || !type) {
            throw DomainError.invalid("MISSING_REQUIRED_FIELDS");
        }

        const result = await saveDraft({
            contentId: contentId ?? null,
            authorId,
            title,
            delta,
            type,
            thumbnailMediaId,
            categoryId: categoryId ?? null
        });

        res.status(200).json({
        data: result,
        });
    },

    async loadDraftController(req, res) {
    
        const contentId = req.params.contentId;
        const authorId = req.user.id;

        if (!contentId) {
            throw DomainError.invalid("MISSING_CONTENT_ID");
        }

        const draft = await loadDraft({ contentId: Number(contentId), authorId });

        if (!draft) {
            throw DomainError.notFound("DRAFT_NOT_FOUND");
        }

        res.status(200).json({ data: draft });
    
    },

    async loadAuthorDraftController(req, res) {
    
        const authorId = req.user.id;

        const draft = await loadAuthorDrafts( authorId );

        if (!draft) {
            res.status(200).json({
                status:true,
                data:[],
            })
        }
        else{
            res.status(200).json({ 
                status:true,
                data: draft
            });
        }

        
    
    },

async publishContentController(req, res) {
    const contentId = req.params.contentId;
    const authorId = req.user.id;

    if (!contentId) {
      return res.status(400).json({ message: "Invalid content id" });
    }
    console.log("Publish Article : ",contentId,authorId)

    await publishContentService({ contentId:Number(contentId), authorId });

    res.status(200).json({ message: "Content published" });
},

async getPublishedContentsController(req, res) {
    const contents = await getPublishedContents();
    res.status(200).json({ data: contents });
    
},
async getMyPublishedContentsController(req, res) {
    const userId = req.user.id
    const contents = await getMyPublishedContent(userId);
    res.status(200).json({ data: contents });
    
},

async resolveMediaController(req, res) {
  try {
    const { mediaIds } = req.body;

    const media = await resolveMedia({ mediaIds });

    res.status(200).json({
      data: media,
    });
  } catch (err) {
    next(err);
  }
},
async getMediaByIdController(req,res){
    const {id} = req.params
    const media= await getMediaByIdService(Number(id))
    res.status(200).json({
        data:media
    })
},
async getPublishedContentByCategorySlugController(req,res){
    const {slug} = req.params
    if(!slug){
        throw DomainError.invalid("Slug is recquired")
    }
    const result= await getPublishedByCategorySlug(slug)
    res.status(200).json({
        data:result
    })
},

async deletePublishedController(req,res){
    const {id} = req.query
    const result = await deletePublishedService(parseInt(id))
    res.status(200).json({
        status:true
    })
},


async deleteDraftController(req,res){
    const {contentId} = req.query
    const authorId = req.user.id

    if(!contentId){
        throw DomainError.invalid("Content Id is required")
    }

    const result = await deleteAuthorDraftService(Number(contentId));
    res.status(200).json({
        status:result
    })
},

}
export {ContentController}