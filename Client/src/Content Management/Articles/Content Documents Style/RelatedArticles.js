// RelatedArticles.js
import { ArticleCard } from "./article card/ArticleCard";
import "./RelatedArticles.css";

export default function RelatedArticles({
  title = "Related articles",
  articles = [],
}) {
    console.log("Artickle that are related metadata",articles)
  if (!articles.length) return null;

  return (
    <section className="related-articles">
      <h2 className="related-articles__title">
        {title}
      </h2>

      <div className="related-articles__list">
        {articles.map(article => (
          <ArticleCard
            key={article.content_id}
            article={article}
          />
        ))}
      </div>
    </section>
  );
}