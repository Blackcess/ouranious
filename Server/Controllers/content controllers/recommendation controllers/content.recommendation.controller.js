// recommendation.controller.js
import { RecommendationService } from "../../../Models/content models/Recommendation model/services/recommendation.service.js";

export async function getRecommendations(req, res) {
 
    const {
      context,
      categoryId,
      authorId,
      excludeContentId,
      limit,
    } = req.query;
    
    // console.log("Request Query is ",(req.query))

    const recommendations =
      await RecommendationService.recommendArticles({
        context,
        categoryId: categoryId ? Number(categoryId) : undefined,
        authorId: authorId ? Number(authorId) : undefined,
        excludeContentId: excludeContentId
          ? Number(excludeContentId)
          : undefined,
        limit: limit ? Number(limit) : undefined,
      });

    res.status(200).json({
      data: recommendations,
    })
}