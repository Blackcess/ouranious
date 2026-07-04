// content.service.js
import {ContentRepository} from "../repository/content.repository.js";
import { deltaToContentDocument } from "../tools/deltaToContentDocument.js";
import { DomainError } from "../../../../Domain Errors/domainErrors.js";
import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";
import { getMediaByIds } from "../../../media models/repository/media.repository.js";
import { getMediaById } from "../../../media models/repository/media.repository.js";
import { CategoryRepository } from "../../../category models/repositories/category.repository.js";

function generateSlug(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
}


//get content by slug
export async function getContentBySlug(slug) {
  if (!slug || typeof slug !== "string") {
    throw DomainError.invalid("SLUG_IS_REQUIRED");
  } 
  const content =  await ContentRepository.findBySlug(slug);
  if (!content) {
    throw DomainError.notFound("CONTENT_NOT_FOUND");
  }
  return content;
}
//get content by id
export async function getContentById(contentId) {
  if (!contentId || typeof contentId !== "number") {
    throw DomainError.invalid("CONTENT_ID_IS_REQUIRED");
  } 
  const content =  await ContentRepository.findById(contentId);
  if (!content) {
    throw DomainError.notFound("CONTENT_NOT_FOUND");
  }
  return content;
}

export async function saveDraft({
  contentId,
  authorId,
  title,
  delta,
  type,
  thumbnailMediaId,
  categoryId
}) {
  let finalContentId = contentId;

  // New content: create content row first
  if (!finalContentId) {
    let slug = generateSlug(title);
    //check if slug exist in DB
    const content =  await ContentRepository.findBySlug(slug);
    if(content){
      slug = slug + Date.now()
    }

    finalContentId = await ContentRepository.createDraftContent({
      title,
      slug,
      authorId,
      type,
      categoryId 
    });
  }

  // Save or replace draft
  await ContentRepository.upsertDraft({
    contentId: finalContentId,
    authorId,
    title,
    delta,
    type,
    thumbnailMediaId,
    categoryId
  });

  return {
    contentId: finalContentId,
    lastSavedAt: new Date().toISOString(),
  };
}

export async function loadDraft({ contentId, authorId }) {
  if (!contentId) return null;

  const draft = await ContentRepository.getDraftByContentId({ contentId, authorId });

  if (!draft) return null;

  return {
    contentId: draft.contentId,
    title: draft.title,
    delta: draft.delta,
    type: draft.type,
    lastSavedAt: draft.updatedAt,
    thumbnailMediaId: draft.thumbnailMediaId,
    categoryId:draft.categoryId
  };
}
export async function loadAuthorDrafts(authorId) {

  const draft = await ContentRepository.getAllAuthorDrafts(authorId);

  if (!draft) return null;

  // return {
  //   contentId: draft.contentId,
  //   title: draft.title,
  //   delta: draft.delta,
  //   type: draft.type,
  //   lastSavedAt: draft.updatedAt,
  //   thumbnailMediaId: draft.thumbnailMediaId,
  //   categoryId:draft.categoryId
  // };
  return draft
}

export async function publishContentService({ contentId, authorId }) {
  const draft = await ContentRepository.getDraftForPublish({
    contentId,
    authorId,
  });

  if (!draft) {
    throw DomainError.notFound("DRAFT_NOT_FOUND");
  }

  if(!draft.categoryId){
    throw DomainError.invalid("No Assigned Category To This Article")
  }


  const document = deltaToContentDocument(draft.delta);

  if (!document.blocks.length) {
    throw DomainError.invalid("CONTENT_MUST_CONTAIN_AT_LEAST_ONE_BLOCK");
  }
 
  const transaction_connection = await connection.getConnection();
  await transaction_connection.beginTransaction();

  try {
    await ContentRepository.publishContent(transaction_connection,{
      contentId,
      title: draft.title,
      blocks: document,
      thumbnailMediaId: draft.thumbnailMediaId ?? null,
      categoryId: draft.categoryId
    });

    await ContentRepository.deleteDraft(transaction_connection,{ contentId, authorId });

    await transaction_connection.commit();
  } catch (err) {
    await transaction_connection.rollback();
    throw err;
  } finally {
    transaction_connection.release();
  }
}

export async function getPublishedContents() {
  const contents = await ContentRepository.getPublishedContents();
  return contents;
}
export async function getMyPublishedContent(userId) {
  const contents = await ContentRepository.getMyPublishedContent(userId);
  return contents;
}

export async function resolveMedia({ mediaIds }) {
  if (!Array.isArray(mediaIds)) {
    throw DomainError.invalid("mediaIds must be an array");
  }

  // Deduplicate + sanitize
  const uniqueIds = [...new Set(mediaIds)]
    .map((id) => Number(id))
    .filter(Boolean);

  if (uniqueIds.length === 0) {
    return [];
  }

  const media = await getMediaByIds(uniqueIds);
  return media;
}

export async function getMediaByIdService(id){
  if(!id){
    throw DomainError.invalid("MEDIA_ID_MISSING")
  }
  const media= await getMediaById(id)
  return media
} 

export async function getPublishedByCategorySlug(slug) {
  //validate category exists
  if(!await CategoryRepository.getCategoryBySlug(slug)){
    throw DomainError.notFound("CATEGORY DOES NOT EXIST")
  }
  //fetch the articles
  const published = await ContentRepository.getPublishedContentByCategorySlug(slug)
  return published
}


export async function deletePublishedService(id){
  const result = await ContentRepository.deletePublished(id) 
  return result
}


export async function deleteDraftService(id){
  const result = await ContentRepository.deleteDraft(id)
  return result
}


export async function deleteAuthorDraftService(contentId){
  const result = await ContentRepository.deleteAuthorDraft(contentId)
  return result
}