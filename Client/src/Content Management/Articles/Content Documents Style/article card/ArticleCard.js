import { Link, NavLink } from "react-router-dom";
import ArticleThumbnail from "../Thumbnails/Article Thumbnail/ArticleThumbnail";
import "./ArticleCard.css"

export function ArticleCard({ article }) {
  return (
    <NavLink
      to={`/view/${article.slug}`}
      className="article-card"
    >
      
        <div className="article-card-thumb">
          {article.thumbnailMediaId ? (
            <ArticleThumbnail mediaId={article.thumbnailMediaId} />
          )
          :
          <img 
            className="article-thumbnail"
            src="https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/0c/8f/45/df/8e/v1_E10/E10AH8F9.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=fd9af3508a33934674a2d996d76fbef316e98d8355577a1f67c8a973335e6f88"
            />
          }
        </div>
      

      <div className="article-card-body">

        <h6 className="article-card-category">
          {article.category_name}
        </h6>
        <h2 className="article-card-title">
          {article.title}
        </h2>

        <time className="article-card-date">
          {new Date(article.updated_at).toLocaleDateString()}
          {"  -  "}
          {article.author}
        </time>
      </div>
    </NavLink>
  );
}
