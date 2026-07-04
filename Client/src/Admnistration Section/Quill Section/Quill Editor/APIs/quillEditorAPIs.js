import axios from "axios";


const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const api = axios.create({
  baseURL: API_BASE_URL, // or your API_BASE_URL
  withCredentials: true
});

// Create Content
export const createContent = async ({
    title,
    delta,
    type,
    status
  }) => {
    const res = await api.post(`/content`, {
          title,
          delta,
          type,
          status
        });
      return res.data.data;
}

// Update Content
export const updateContent = async ({
  contentId,
  title,
  delta,
  status
}) => {
  const res = await api.put(`/content/${contentId}`, {
    title,
    delta,
    status
  });
  return res.data.data;
};

// load draft
export const loadDraft = async (contentId) => {
  const res = await api.get(`/content/draft/${contentId}`);
  return res.data.data;
};

//save draft
export const saveDraft = async ({
  contentId,
  title,
  delta,
  type,
  thumbnailMediaId,
  categoryId

}) => {
  console.log("Draft Debbugg=>",thumbnailMediaId)
  const res = await api.post("/content/draft", {
    contentId,
    title,
    delta,
    type,
    thumbnailMediaId,
    categoryId
  });

  return res.data.data;
};
// publish content
export const publishContent = async (contentId) => {
  const res = await api.post(`/content/${contentId}/publish`);
  return res.data;
}

//upload image
export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("image", file);

  const res = await api.post("/media/upload", formData);
  // console.log("Uploaded IOmage is",res.data.data)
  return res.data.data; // { mediaId, url }
};

//list media
export const listMedia = async () => {
  const res = await api.get("/media");
  return res.data.data;
};
//list all categories
export const getAllCategories = async ()=>{
  const res = await api.get("/category/")
  return res.data.data
}
//get a category by id
export const getCategoryById = async (id)=>{
  const res = await api.get(`/category/id/${id}`)
  return res.data.data
}
//get a category by slug
export const getCategoryBySlug = async (slug)=>{
  const res = await api.get(`/category/slug/${slug}`)
  return res.data.data
}