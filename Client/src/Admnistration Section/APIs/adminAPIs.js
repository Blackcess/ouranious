import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const getMyPublishedContent = async ()=>{
    const res = await api.get(`/content/all/my-published`)
    return res.data.data
}

export const deletePublishedArticle  = async (id)=>{
  const res = await api.delete(`/content/published?id=${id}`)
  return res.data
} 

export const getAuthorDrafts = async ()=>{
  const res = await api.get(`/content/all/drafts`)
  return res.data.data
}


export const deleteDraftArticle  = async (contentId)=>{
  const res = await api.delete(`/content/draft?contentId=${contentId}`)
  return res.data
}