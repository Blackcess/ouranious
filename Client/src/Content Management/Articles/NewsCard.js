import React, { useState } from "react";
import "./NewsCard.css";
import { useEffect, useRef } from "react";
import axios from "axios";
import { NavLink } from "react-router-dom";



const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
const NewsCard = () => {

  const [content,setContent] = useState({ })
  const [contentLoaded,setContentLoaded] = useState(false);

  useEffect(()=>{
    getContent();
  },[])
  const getContent = async()=>{    //by slug
    try {
        const res= await axios.get(`${API_BASE_URL}/content`,{
        withCredentials:true
      })
      
       
        if(res.data.status){
          //  console.log("Article content is: ",res.data.data)
           setContent(res.data.data[1])
           setContentLoaded(true)
        }
      
    } catch (error) {
      console.log(error)
    }
  }
  return (<>
  { (contentLoaded) && 
    <NavLink  className="news-card" to={`/ourans-platform/contact#intro`}>
      <img src={
      (() => {
        const coverImage = content.media.find(m => m.attribute === 'thumbnail');
        return coverImage
          ? coverImage.file_path
          : "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/5d/0e/4d/1f/68/v1_E10/E1028W21.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=aac5c205833748eca936d3110f7989032243975483e7716ce5f5492796818e32";
      })()
    } alt={content.title} className="news-thumbnail" />
      <div className="news-content">
        <h2 className="news-title">{content.title}</h2>
        <p className="news-description">This is a news article</p>
        <div className="news-meta">
          <span>{content.author}</span>
          <span>{content.date}</span>
        </div>
      </div>
    </NavLink>
}
    </>
  );
};

export default NewsCard;