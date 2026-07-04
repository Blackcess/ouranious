import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Get content by slug
export async function getContentBySlug(slug) {
  const res = await api.get(`/content/${slug}`);
  return res.data.data;
}

export async function getContentById(contentId) {
  const res = await api.get(`/content/${contentId}`);
  return res.data.data;
}

export async function getPublishedContents() {
  const res = await api.get(`/content/all/published`);
  return res.data.data;
}

export async function getResolvedMediabyId(mediaIds){
  const res = await api.post(`/content/media/resolve`,{
    mediaIds
  })
  return res.data.data
}

export async function getMediaById(id) {
  const res = await api.get(`/content/media/${id}`)
  return res.data.data
}
export async function getCategoryById(id){
  const res = await api.get(`/category/id/${id}`)
  return res.data.data
} 
export async function getCategoryBySlug(slug){
  const res = await api.get(`/category/slug/${slug}`)
  return res.data.data
} 
export async function getContentByCategory(slug){
  const res = await api.get(`/content/category/slug/${slug}/published`)
  return res.data.data
} 
//recommendation center
export async function getArticleRecommendations(contentId,categoryId,authorId){
  const excludeContentId = contentId
  const res = await api.get(`/content/recommendations?context=article&excludeContentId=${excludeContentId}&categoryId=${categoryId}&authorId=${authorId}`)
  return res.data.data
}
//post comment
export async function postComment(contentId,commentText){
  const res = await api.post(`/content/comment`,{
    content_id:contentId,
    comment:commentText
  })
  return res.data.data
}
//get comments
export async function getComments(contentId){
  const res = await api.get(`/content/${contentId}/comments`)
  return res.data.data
}
//delete comment
export async function deleteComment(commentId){
  const res = await api.delete(`/content/comment/${commentId}`)
  return res.data.data
}

