// category.service.js
import { CategoryRepository } from "../repositories/category.repository.js";
import { DomainError } from "../../../Domain Errors/domainErrors.js";

export const CategoryService = {
  async listAllCategories() {
    const categories = await CategoryRepository.listAllCategories();
    return categories;
  },

  async getCategoryById(categoryId) {
    if (!categoryId || typeof categoryId !== "number") {
      throw DomainError.invalid("CATEGORY_ID_IS_REQUIRED");
    }

    const category = await CategoryRepository.getCategoryById(categoryId);

    if (!category) {
      throw DomainError.notFound("CATEGORY_NOT_FOUND");
    }

    return category;
  },

  async getCategoryBySlug(slug) {
    if (!slug || typeof slug !== "string") {
      throw DomainError.invalid("CATEGORY_SLUG_IS_REQUIRED");
    }

    const category = await CategoryRepository.getCategoryBySlug(slug);

    if (!category) {
      throw DomainError.notFound("CATEGORY_NOT_FOUND");
    }

    return category;
  },
};