import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getContentBySlug,getCategoryById, getContentByCategory, getArticleRecommendations} from "./APIs/contentDocumentAPI";
import ArticleView from "./ArticleViewer";
import "./ArticleViewPage.css"
import RelatedArticles from "./RelatedArticles";

export default function ArticleViewPage() {
  const { slug } = useParams();

  const [content, setContent] = useState(null);
  const [category,setCategory] = useState(null)
  const [loading, setLoading] = useState(true);
  const [articles,setArticles] = useState(null)
  const [error, setError] = useState(null);
  

  useEffect(() => {
    let mounted = true;

    async function loadContent() {
      try {
        setLoading(true);
        const data = await getContentBySlug(slug);
        const categoryData = await getCategoryById(data.categoryId)
        const relatedArticles = await getArticleRecommendations(data.content_id,data.categoryId,data.authorId)
        setArticles(relatedArticles)
        // console.log("Fetched related Articles:", relatedArticles);
        setCategory(categoryData)
        if (mounted) setContent(data);
      } catch (err) {
        console.error(err);
        if (mounted) setError("Failed to load article");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadContent();
    return () => {
      mounted = false;
    };
  }, [slug]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!content) return <p>Article not found</p>;

  return <>
      <section className="view-page-temp">
        <ArticleView content={content} category={category}/>
        <RelatedArticles articles={articles}/>
      </section>
  </>
}
