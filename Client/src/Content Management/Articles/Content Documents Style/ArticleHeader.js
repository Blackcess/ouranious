import React from "react";
import ArticleThumbnail from "./Thumbnails/Article Thumbnail/ArticleThumbnail";
import "./ArticleHeader.css"
import { NavLink } from "react-router-dom";

export default function ArticleHeader({ title, author, updatedAt,thumbnailMediaId,category }) {
 return (
    <header className="article__header">
          <NavLink
            to={`/category/${category.categoryId}`}
            className="article__category"
          >
            {category.name}
          </NavLink>
          {thumbnailMediaId && (
            <ArticleThumbnail mediaId={thumbnailMediaId} />
          )}

          <h1 className="article__title">{title}</h1>

          <div className="article__meta">
            {author && <span className="article__author">{author}{" "}•{" "}</span>}
            {updatedAt && (
              <time
                className="article__date"
                dateTime={updatedAt}
              >
                {new Date(updatedAt).toLocaleDateString()}
              </time>
            )}
          </div>
    </header>
  );
}
