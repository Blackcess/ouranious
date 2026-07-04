// recommendation.service.js
import { RecommendationRepository } from "../Repository/recommendation.repository.js";
import { DomainError } from "../../../../Domain Errors/domainErrors.js";

const DEFAULT_LIMITS = {
  article: 4,
  category: 20,
  author: 10,
  home: 10,
};

export const RecommendationService = {
  /**
   * Canonical recommendation entry point
   */
  async recommendArticles({
    context,
    categoryId,
    authorId,
    excludeContentId,
    limit,
  }) {
    
    switch (context) {
      case "article":
        return recommendForArticle({
          categoryId,
          authorId,
          excludeContentId,
          limit,
        });

      case "category":
        return recommendForCategory({
          categoryId,
          limit,
        });

      case "author":
        return recommendForAuthor({
          authorId,
          limit,
        });

      case "home":
        return recommendForHome({
          limit,
        });

      default:
        throw DomainError.invalid("INVALID_RECOMMENDATION_CONTEXT");
    }
  },
};

/* ---------------- Context-specific handlers ---------------- */

async function recommendForArticle({
  categoryId,
  authorId,
  excludeContentId,
  limit,
}) {
  
  if (!categoryId || typeof(categoryId) !== "number") {
    throw DomainError.invalid("CATEGORY_ID_REQUIRED");
  }

  if (!excludeContentId || typeof excludeContentId !== "number") {
    throw DomainError.invalid("CONTENT_ID_REQUIRED");
  }

  // authorId is optional (guest authors, legacy content)
  const finalLimit = limit ?? DEFAULT_LIMITS.article;

  return RecommendationRepository.getRelatedByCategory({
    categoryId,
    authorId: authorId ?? null,
    excludeContentId,
    limit: finalLimit,
  });
}

async function recommendForCategory({
  categoryId,
  limit,
}) {
  if (!categoryId || typeof categoryId !== "number") {
    throw DomainError.invalid("CATEGORY_ID_REQUIRED");
  }

  const finalLimit = limit ?? DEFAULT_LIMITS.category;

  return RecommendationRepository.getByCategory({
    categoryId,
    limit: finalLimit,
  });
}

async function recommendForAuthor({
  authorId,
  limit,
}) {
  if (!authorId || typeof authorId !== "number") {
    throw DomainError.invalid("AUTHOR_ID_REQUIRED");
  }

  const finalLimit = limit ?? DEFAULT_LIMITS.author;

  return RecommendationRepository.getByAuthor({
    authorId,
    limit: finalLimit,
  });
}

async function recommendForHome({ limit }) {
  const parsedLimit = Number(limit ?? DEFAULT_LIMITS.home);

  if (!Number.isInteger(parsedLimit) || parsedLimit <= 0) {
    throw DomainError.invalid("INVALID_HOME_FEED_LIMIT");
  }

  return RecommendationRepository.getHomeFeed({
    limit: 10,
  });
}