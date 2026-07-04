import ArticleThumbnail from "../../../../Content Management/Articles/Content Documents Style/Thumbnails/Article Thumbnail/ArticleThumbnail";
import "./AdminArticleCard.css"
import { RiDeleteBin5Line } from "react-icons/ri";
import { CiEdit } from "react-icons/ci";
import { useNavigate } from "react-router-dom";



export function AdminArticleCard({article, onDelete, type}){
    const navigation = useNavigate()

    return (
    <section
      className="admin-type-card"
    >
      <div className="admin-card-details">

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
                {article.author_name}
            </time>

        </div>
      </div>

      <div className="article-admin-prev">
            <RiDeleteBin5Line
            className="admin-icon"
            onClick={()=>{
              onDelete(article.content_id)
            }}
          />
          
          { (type === "published") ?
            <p 
              className="read-me-tag"
              onClick={()=>{
                navigation(`/view/${article.slug}`)
              }}
            >
              read_me
            </p>
            :
            <CiEdit
              className="admin-icon"
              onClick={()=>{
                navigation(`/uploads?contentId=${article.content_id}`)
              }}  
            /> 
          }

      </div>
        
    </section>
  );
} 