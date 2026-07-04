import React from "react";
import ContentRenderer from "../../../Renderer/ContentRenderer";
import { getResolvedMediabyId } from "./APIs/contentDocumentAPI";
import { useEffect } from "react";
import { useState } from "react";
import ArticleCommentsSection from "./comments/Comment Parent Wrapper/ArticleCommentWrapper";


export default function ArticleBody({ document, contentId, redirect=null}) {

  const [mediaMap, setMediaMap] = useState({});
  const [loading,setLoading] = useState(true)
  
  useEffect(() => {
    
    const mediaIds = extractMediaIds(document);
    

    if (mediaIds.length === 0) {
      setMediaMap({});
      setLoading(false)
      return;
    }

    async function loadMedia() {
      try {
        const mediaList = await getResolvedMediabyId(mediaIds);

        const map = {};
        // console.log("Media List is",mediaList)
        mediaList.forEach((m) => {
          map[m.media_id] = m;
        });

        setMediaMap(map);
        
      } catch (error) {
        console.error(error)
      }
      finally{
        setLoading(false)
      }
  }

  loadMedia();
}, [document]);
  function extractMediaIds(document) {
    if (!document || !Array.isArray(document.blocks)) return [];

    return document.blocks
      .filter((block) => block.type === "media")
      .map((block) => block.media_id);
  }
  if(loading){
    return <p>Loading...</p>
  }
  return (
    <section className="article__body">
      <ContentRenderer 
        document={document} 
        mode="public"
        mediaMap={mediaMap} 
      
      />
      <ArticleCommentsSection contentId={contentId} redirect={redirect} />
    </section>
  );
}
