import { useEffect, useRef, useState } from "react";
import "./SampleArticle.css";
import { getPublishedContents } from "./Content Documents Style/APIs/contentDocumentAPI";
import { NavLink } from "react-router-dom";

export default function ArticleLayout() {
  const [loading, setLoading] = useState(true);
  const [contents, setContents] = useState([]);

  useEffect(() => {
    const fetchContents = async () => {
      try {
        const data = await getPublishedContents();
        setContents(data);
        console.log("Sample Articles are",data)
      } catch (error) {
        console.error("Error fetching contents:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchContents();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="layout">
      <h1>Published Articles</h1>
      {
      contents.length === 0 ? 
      (
        <p>No published articles available.</p> 
      ) 
      : 
      (
        contents.map((content) => (
          <div key={content.contentId} className="article-summary"> 
            <NavLink to ={`/view/${content.slug}`}>{content.title}</NavLink>
          </div>
        )
      )
    )
      }

    </div>
        
  );
}


