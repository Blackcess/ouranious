import { useEffect, useRef, useState } from "react";
import "./SampleArticle.css";
import {styled} from "styled-components";
import axios from "axios";
import NewsCard from "./NewsCard";
import useExtractHeadings from "../../component utils/heading parser for TOC/extractTOC";
import { useLocation } from "react-router-dom";


const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
export default function ArticleLayout() {

  const [content,setContent] = useState({ })
  const [contentLoaded,setContentLoaded] = useState(false);
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const slug = searchParams.get('slug');
  

  useEffect(()=>{
    getContent();
  },[])
  const extractedHeadings = useExtractHeadings(content.body);
  const getContent = async()=>{    //by slug
    try {
        const res= await axios.get(`${API_BASE_URL}/content/${slug}`,{
        withCredentials:true
      })
    
      if(res.data.status){
           console.log("Article content is: ",res.data.data)
           setContent(res.data.data)
           setContentLoaded(true)
        }
    } catch (error) {
      console.log(error)
    }
  }
  function renderBody(body, media) {
  // Replace [media attribute="media1"] with actual <img>
  return body.replace(/\[media attribute="(.+?)"\]/g, (match, attribute) => {
    const mediaImg = media?.find(m => m.attribute === attribute);
    const url = mediaImg
      ? mediaImg.file_path
      : "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/5d/0e/4d/1f/68/v1_E10/E1028W21.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=aac5c205833748eca936d3110f7989032243975483e7716ce5f5492796818e32"
    return `<img src="${url}" alt="${attribute}" class="article-inline-image"/>`;
  });
}

// useEffect(()=>{
//   console.log("My Content Creation Carrer is ",content)
// },[contentLoaded])


   


  return (
    
    <div className="layout">
        {/* Table   Of Content */}
      <TableOfContents body={content.body}/>
      {/* Actual Article */}

      <div className="article-container">
        {/* Title */}
        <h1 className="article-title" id="intro">{content.title}</h1>

        {/* Author & Meta */}
        <div className="article-meta">
          <span className="author">{content.author}</span>
          <span className="dot">•</span>
          <span className="date">
            {new Date(content.published_at).toLocaleDateString()}
          </span>
        </div>

        {/* Cover Image */}
       {content.media ? (
  <img
    src={
      (() => {
        const coverImage = content.media.find(m => m.attribute === 'coverImage');
        return coverImage
          ? coverImage.file_path
          : "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/5d/0e/4d/1f/68/v1_E10/E1028W21.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=aac5c205833748eca936d3110f7989032243975483e7716ce5f5492796818e32";
      })()
    }
    alt="coverimage"
    className="article-cover"
  />
) : (
  <p>Loading cover image...</p>
)}
        {/* Article Body */}
        {(contentLoaded) ?<div
          className="article-body"
          dangerouslySetInnerHTML={{ __html: renderBody(content.body, content.media) }}
        />
      :
      <p>Loading...</p>}
        {/* Tags & Categories */}
        <div className="article-tags">
          {content.categories?.map((cat,index) => (
            <span key={index} className="category">
              {cat.category}
            </span>
          ))}
          {content.tags?.map((tag,index) => (
            <span key={index} className="tag">
              #{tag.tag}
            </span>
          ))}
        </div>

        {/* Comments Placeholder */}
        <div className="article-comments">
          <h2>Comments</h2>
          <p>Comments section coming soon...</p>
        </div>
      </div>
      <div className="related-articles">
        <h2>Related Articles</h2>
        <div className="related-articles-list">
          <NewsCard/>
          <NewsCard/>
          <NewsCard/>
        </div>
      </div>
    </div>
  );
}

// Table of Content
function TableOfContents({ body }) {
  const headings = useExtractHeadings(body);
  const [activeId, setActiveId] = useState(null);

  useEffect(() => {
    if (!headings.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      {
        rootMargin: "-100px 0px -70% 0px", 
        threshold: 0.3,
      }
    );

    headings.forEach(h => {
      const el = document.getElementById(h.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [headings]);

  const handleClick = (e, id) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      const yOffset = -70; // adjust for sticky header
      const y = el.getBoundingClientRect().top + window.scrollY + yOffset;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  return (
    <nav className="toc">
      <h3>Table of Contents</h3>
      <ul>
        {headings.map(h => (
          <li key={h.id} className={`${h.level} ${activeId === h.id ? "active" : ""}`}>
            <a href={`#${h.id}`} onClick={(e) => handleClick(e, h.id)}>
              {h.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
