import { useEffect, useState } from "react";
import { ArticleCard } from "../../article card/ArticleCard";
import "./CategoryPage.css"
import { useLocation, useParams } from "react-router-dom";
import { getCategoryById, getContentByCategory } from "../../APIs/contentDocumentAPI";
import ShimmerLoader from "../../../../../Util Components/ShimmerLoader/ShimmerLoader";


export function CategoryPageWrapper(){
  const [category,setCategory] = useState(null)
  const [articles,setArticles] = useState(null)
  const [loading,setLoading] = useState(true)
  const {id} = useParams()

  useEffect(()=>{
    const loadData = async ()=>{
      try {
        const categoryData = await getCategoryById(parseInt(id))
        setCategory(categoryData)
        // console.log("My Articles",categoryData)
        if(categoryData){
          const categoryArticles = await getContentByCategory(categoryData.slug)
          setArticles(categoryArticles)
          
        }
        
      } catch (error) {
        console.error(error)
      }
      finally{
        setLoading(false)
      }
    }
    loadData()
  },[])
  if(loading){
    return <>
      <section className="category-loading-page">
        <ShimmerLoader/>
      </section>
    </>
    
  }
  return <>
    <section className="category-page-wrapper">
      <CategoryPage category={category} articles={articles}/>
    </section>
  </>
}



export function CategoryPage({ category, articles }) {
  return (
    <main className="category-page">
      <header className="category-header">
        <h1 className="category-title">{category.name}</h1>
        {category.description && (
          <p className="category-description">
            {category.description}
          </p>
        )}
      </header>

      <section className="article-list">
        {articles.length === 0 ? (
          <p className="empty-state">
            No articles in this category yet.
          </p>
        ) : (
          articles.map(article => (
            <ArticleCard
              key={article.content_id}
              article={article}
            />
          ))
        )}
      </section>
    </main>
  );
}


