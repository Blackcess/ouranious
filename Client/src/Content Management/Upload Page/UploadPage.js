import React, { useEffect, useState } from "react";
import "./UploadPage.css"
import {motion}  from "framer-motion"
import axios from "axios";

const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
export default function ArticleUpload() {
  const [formData, setFormData] = useState({
    title: "",
    slug: "",
    body: "",
    coverImage: "",
    authorId: "",
    category: "",
    tags:"",
    status: "draft",
    media:[] // list of media objects {type,attribute,caption,url}
  });

  const [addedMedia,setAddedMedia] = useState([]) // list of media objects {type,attribute,caption,url}

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  // update the formData everytime the addedMedia list is updated
  useEffect(()=>{
    setFormData({...formData,media:addedMedia})
  },[addedMedia])

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE_URL}/post/all`,{
        ...formData
      },
       {
        withCredentials:true
      });
      if (res.data.status) {
        alert("✅ Article uploaded successfully!");
        setFormData({
          title: "",
          slug: "",
          body: "",
          coverImage: "",
          authorId: "",
          category: "",
          tags:"",
          status: "draft",
        });
        setAddedMedia([])
      } else {
        alert("❌ Failed to upload article.");
      }
    } catch (error) {
      console.error(error);
      alert("⚠️ Server error.");
    }
  };

  return (
    <div className="upload-container">
      <h1>Upload New Article</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <label>Title</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
        />

        <label>Slug</label>
        <input
          type="text"
          name="slug"
          value={formData.slug}
          onChange={handleChange}
          placeholder="e.g. the-future-of-ouranious"
          required
        />

        <label>Body (HTML content)</label>
        <textarea
          name="body"
          value={formData.body}
          onChange={handleChange}
          rows="10"
          placeholder="<h2>Intro</h2><p>Write your article here...</p>"
          required
        />
        <label>Intro Image</label>
        <input
          type="text"
          name="coverImage"
          value={formData.coverImage}
          onChange={handleChange}
          placeholder="https://example.com/image.jpg"
        />
        <AddMoreMedia value={{addedMedia,setAddedMedia}}/>

        <label>Author ID</label>
        <input
          type="number"
          name="authorId"
          value={formData.authorId}
          onChange={handleChange}
          required
        />

        <label>Category</label>
        <input
          type="text"
          name="category"
          value={formData.category}
          onChange={handleChange}
          placeholder="Technology, Startups..."
        />
        <label>Tags</label>
        <input
          type="text"
          name="tags"
          value={formData.tags}
          onChange={handleChange}
          placeholder="Insert Tags separated by commas"
        />

        <label>Status</label>
        <select name="status" value={formData.status} onChange={handleChange}>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
          <option value="archived">Archived</option>
        </select>
    

        <button type="submit">Submit Article</button>
      </form>
    </div>
  );
}

function AddMoreMedia({value}){
  const [mediaType,setMediaType] = useState("image")
  const [mediaAttribute,setMediaAttribute] = useState("inlineImage")
  
  const [mediaCaption,setMediaCaption] = useState("")
  const [captionError,setCaptionError] = useState("")
  const [imageUrl,setImageUrl] = useState("")
  const [videoUrl,setVideoUrl] = useState("")
  const [audioUrl,setAudioUrl] = useState("")
  // validation for the media that is added to the addedMedia list
  function validateMediaString(input) {
    // ^media\d+$ → string must start with "media", followed by one or more digits
    const pattern = /^media\d+$/;
    return pattern.test(input);
  }


  return (
    <>
      <section className="media-section">
      <h2>Additional Media</h2>
      <div className="media-form">
        <label>Media URL</label>
        <input type="text" name="mediaUrl" placeholder="https://example.com/media.jpg" value={imageUrl} onChange={(e)=>setImageUrl(e.target.value)}/>         
        <label>Type</label>
        <select name="mediaType" onChange={(e)=>setMediaType(e.target.value)} value={mediaType}>
          <option value="image" >Image</option>
          <option value="video">Video</option>
          <option value="audio">Audio</option>
        </select>
        <label>Attribute</label>
        {(mediaType ==="image") ? <select name="mediaAttribute" onChange={(e)=>setMediaAttribute(e.target.value)} value={mediaAttribute}>
          <option value="inlineImage">Inline Image</option>
          <option value="thumbnail">Thumbnail</option>
        </select>
        :
        <p className="media-error">{mediaType}  not supported on this version of Ouranious</p>
      }
        {(mediaAttribute ==="inlineImage") && <div className="media-form-inline">
          <label>Caption*</label>
          <input type="text" name="mediaCaption" placeholder="A descriptive caption for the media" className="desc-in" value={mediaCaption} 
          onChange={(e)=>{
            setMediaCaption(e.target.value)
            if(validateMediaString(e.target.value)){
              setCaptionError("")
            }else{
              setCaptionError("⚠️ Caption must start with 'media' followed by a number, e.g., media1, media2")  
            }
          }}/>
          {captionError && <p className="media-error">{captionError}</p>}
        </div>}
        <button type="button" className="add-media-button" onClick={(e)=>{
          e.preventDefault();
          //I want to add some restrictions to the dia that is added to the addedMedia list
          if(mediaType==="image" && imageUrl.trim()===""){
            alert("⚠️ Please provide a valid image URL.");
            return;
          }
          if(mediaType==="video" && videoUrl.trim()===""){
            alert("⚠️ Please provide a valid video URL.");
            return;
          }
          if(mediaType==="audio" && audioUrl.trim()===""){
            alert("⚠️ Please provide a valid audio URL.");
            return;
          }
          if(mediaAttribute.trim()===""){
            alert("⚠️ Please select a valid media attribute.");
            return;
          }
          if(mediaType==="image" && mediaAttribute==="inlineImage" && mediaCaption.trim()===""){
            alert("⚠️ Please provide a caption for the inline image.");
            return;
          }
          // check if the chosern caption is not already used in the addedMedia list
          if(mediaType==="image" && mediaAttribute==="inlineImage" && value.addedMedia.some(m=>m.caption===mediaCaption.trim())){
            alert("⚠️ Caption already used. Please choose a different caption.");
            return;
          }
          // add to the addedMedia list
          const newMedia = {
            type:mediaType,
            attribute:mediaAttribute,
            caption:(mediaAttribute==="inlineImage")?mediaCaption:"thumbNail",
            url:(mediaType==="image") ? imageUrl : (mediaType==="video") ? videoUrl : audioUrl
          }
          value.setAddedMedia([...value.addedMedia,newMedia])
          setMediaCaption("")
          setImageUrl("")
          setVideoUrl("")
          setAudioUrl("")
          setMediaAttribute("inlineImage")
          setMediaType("image")
        }}>Add Media</button>
      </div>
      {/* When a media is added to the addedMedia list there should be a floating element at the top of the container with the image that is specified by the url */}

      <div className="added-media-list">
        {value.addedMedia.map((media,index)=>(
          <motion.div 
            key={index}
            className="added-media-item"
            initial={{opacity:0, y:-10}}
            animate={{opacity:1, y:0}}
            transition={{duration:0.3, delay:index * 0.1}}
          >
            {(media.type ==="image") && <img src={media.url} alt={media.caption || `Media ${index + 1}`} className="article-media"/>}   
            <div className="media-info">
              <p><strong>Type:</strong> {media.type}</p>
              <p><strong>Attribute:</strong> {media.attribute}</p>
              {media.caption && <p><strong>Caption:</strong> {media.caption}</p>}
              <p><strong>URL:</strong> {media.url}</p>
              <button type="button" className="remove-media-button" onClick={()=>{
                const updatedMedia = value.addedMedia.filter((_,i)=>i!==index)
                value.setAddedMedia(updatedMedia)
              }
              }>Remove</button>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
    </>
  )
}


