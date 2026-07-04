import React from "react";
import ContentRenderer from "../../../Renderer/ContentRenderer";
import ArticleHeader from "./ArticleHeader";
import ArticleBody from "./ArticleBody";
import "./styles/article.public.css";
import "./styles/article.overlays.css";

export default function ArticleView({ content, category}) {
  if (!content) return null;
  console.log("Aricle DOCUMENT METADATA IS ",content)
  const {
    title,
    author_name,
    updated_at,
    content_document,
    thumbnailMediaId
  } = content;

  return (
    <article className="article">
      <ArticleHeader
        title={title}
        author={author_name}
        updatedAt={updated_at}
        thumbnailMediaId={thumbnailMediaId}
        category={category}
        
      />

      <ArticleBody document={content_document} contentId={content.content_id}/>
    </article>
  );
}
