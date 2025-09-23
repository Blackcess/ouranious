import { useState, useEffect } from "react";
import { useRef } from "react";
import "./CategoryTemplate.css";
import { setDragLock } from "framer-motion";
import axios from "axios";
import { useLocation } from "react-router-dom";

const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
const dummyCategory = {
  name: "Technology",
  description: "Latest news, articles, and insights in technology."
};

// const dummyArticles = [
//   {
//     id: 1,
//     title: "AI Revolutionizes Healthcare",
//     excerpt: "Artificial intelligence is transforming healthcare systems worldwide...",
//     author: "Jane Doe",
//     publishedAt: "2025-09-20T10:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/ed/d7/3a/88/80/v1_E10/E107XAGI.JPG?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=52e8f1e658b076232d68f68fb9faf14bfe1a11ad70dace5e5a0ea0b056bda50a",
//     slug: "ai-revolutionizes-healthcare"
//   },
//   {
//     id: 2,
//     title: "Breakthrough in Quantum Computing",
//     excerpt: "Quantum computing takes a major leap forward with new processors...",
//     author: "John Smith",
//     publishedAt: "2025-09-19T12:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/92/80/45/79/0a/v1_E10/E105Y8E1.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=05b049d9ab46467d9d1666d37033208071b9f9707e4f1a1c04d2d86b00dea03d",
//     slug: "breakthrough-in-quantum-computing"
//   },
//   {
//     id: 3,
//     title: "Renewable Energy Trends in 2025",
//     excerpt: "Solar and wind energy continue to grow rapidly across the globe...",
//     author: "Alice Brown",
//     publishedAt: "2025-09-18T15:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/14/9a/6f/03/6b/v1_E11/E117ZKPW.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=5fbe96fa8764f326e08af73547ba37024660ea871fbcc888deec781da0b6253f",
//     slug: "renewable-energy-trends-2025"
//   },
//   {
//     id: 3,
//     title: "Renewable Energy Trends in 2025",
//     excerpt: "Solar and wind energy continue to grow rapidly across the globe...",
//     author: "Alice Brown",
//     publishedAt: "2025-09-18T15:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/14/9a/6f/03/6b/v1_E11/E117ZKPW.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=5fbe96fa8764f326e08af73547ba37024660ea871fbcc888deec781da0b6253f",
//     slug: "renewable-energy-trends-2025"
//   },
//   {
//     id: 3,
//     title: "Renewable Energy Trends in 2025",
//     excerpt: "Solar and wind energy continue to grow rapidly across the globe...",
//     author: "Alice Brown",
//     publishedAt: "2025-09-18T15:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/14/9a/6f/03/6b/v1_E11/E117ZKPW.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=5fbe96fa8764f326e08af73547ba37024660ea871fbcc888deec781da0b6253f",
//     slug: "renewable-energy-trends-2025"
//   },
//   {
//     id: 3,
//     title: "Renewable Energy Trends in 2025",
//     excerpt: "Solar and wind energy continue to grow rapidly across the globe...",
//     author: "Alice Brown",
//     publishedAt: "2025-09-18T15:00:00Z",
//     thumbnail: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/14/9a/6f/03/6b/v1_E11/E117ZKPW.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=5fbe96fa8764f326e08af73547ba37024660ea871fbcc888deec781da0b6253f",
//     slug: "renewable-energy-trends-2025"
//   }
//   // add more dummy articles as needed
// ];
// const dummyPopular = [
//   { id: 1, title: "Top AI Trends in 2025", slug: "top-ai-trends-2025" },
//   { id: 2, title: "Blockchain Beyond Cryptocurrency", slug: "blockchain-beyond-crypto" },
//   { id: 3, title: "5G Networks Expansion", slug: "5g-networks-expansion" }
// ];

// const dummyCategories = [
//   "Technology",
//   "Science",
//   "Health",
//   "Business",
//   "Sports",
//   "Entertainment"
// ];

const CategoryPage = () => {
  const [categoryData, setCategoryData] = useState({});
  const [articles, setArticles] = useState([]);
  const [categoryContent,setCategoryContent] = useState([]); 
  const [categoryLoading,setCategoryLoading] = useState(true);
  const [detailedView,setDetailedView] = useState([]);
  const [detailedViewLoaded,setDetailedViewLoaded] = useState(false); 
  const articleRefs = useRef([]); 
  // get params
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const categoryId = parseInt(searchParams.get('categoryId')) || 44;
  const categoryName = searchParams.get('categoryName') || "Ouranious News";
    // Fetch category data and articles (replace with real API calls)
    const getCategoryContent = async () => {
        try {
            setCategoryLoading(true);
            const res = await axios.get(`${API_BASE_URL}/category/related-content/${categoryId}`, {
                withCredentials: true
            });

            if (res.data.status) {
                console.log("Related Content:  ", res.data);
                setCategoryContent(res.data.data);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setCategoryLoading(false); // ✅ end loading state here
        }
    };
    const getDetailedContentData= async(id)=>{
       
        try {
            const res = await axios.get(`${API_BASE_URL}/content/card/display/${id}`,{
                withCredentials:true
            })
            if(res.data.status){
                setDetailedView(prev=>[...prev,res.data.data])
            }
        } catch (error) {
            console.error(error)
        } 
    }

  // First effect → load category data
  useEffect(() => {
    getCategoryContent();
  }, [categoryId]);

  // Second effect → when categoryContent changes, fetch all details
  useEffect(() => {
    if (categoryContent.length > 0) {
      setDetailedView([]); // reset before refetch
      setDetailedViewLoaded(false);

      // Fetch all details in parallel
      Promise.all(
        categoryContent.map((row) => getDetailedContentData(row.content_id))
      ).then(() => {
        setDetailedViewLoaded(true);
      });
    }
  }, [categoryContent]);

  // Fade-in animation on scroll   
  useEffect(() => {
    const handleScroll = () => {
      articleRefs.current.forEach((el) => {
        if (!el) return; 
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 50) {
          el.classList.add('fade-in');
        }
      });
    };
    window.addEventListener('scroll', handleScroll);
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [articles]);
  useEffect(()=>{
    console.log("Loaded State ",detailedViewLoaded,detailedView)
  })



 return (
    <div className="category-page-wrapper">
      <main className="category-main">
        <div className="category-page-container">
            <header className="category-header">
                <h1>{categoryName}</h1>
                <p>Latest news, articles, and insights in {categoryName}</p>
            </header>

            {(detailedView.length) ? <div className="articles-grid">
                {detailedView.map((article, index) => (
                <div 
                        key={index}
                        className="article-card"
                        ref={(el) => (articleRefs.current[index] = el)} 
                >
                    {(article[0].media) ?(
                        <img
                            src={article[0].media[0].file_path}
                            alt="thumbnail"   
                            className="article-thumbnail"            
                        />  
                       
                    )
                    :
                    <img
                            src={`https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/5b/c6/c8/61/72/v1_E10/E104FVXR.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=77c12d039d04192c6e452c73a15c536409906f296a4a9c6345e204a13396e591`}
                            alt="thumbnail"   
                            className="article-thumbnail"            
                        />  
                    }    
                    <div className="overlay">
                        <a href={`article/news?slug=${article[0].slug}`} className="read-more-overlay">
                            Read More
                        </a>
                    </div>   
                    <div className="article-content">
                        <h2 className="article-title">{article[0].title}</h2>  
                        <p className="article-excerpt">{}</p>
                        <div className="article-meta">  
                            <div>By {article[0].author}</div> | {" "}
                            {(article[0].published_at) && <div>{article[0].published_at.split("T")[0]}</div>}
                        </div> 
                    </div>    
                </div>         
                ))}    
            </div>
            : (categoryLoading ? <p>Loading...</p> : <p>No articles found in this category.</p>)
            }  
       {/* Please Render ORE data  */}
    </div>
      </main>

      {/* <aside className="category-sidebar">
        <section className="sidebar-section">
          <h3>Popular Articles </h3>
          <ul>
            {dummyPopular.map((item) => (
              <li key={item.id}>
                <a href={`/articles/${item.slug}`}>{item.title}</a>
              </li>
            ))}
          </ul>
        </section>

        <section className="sidebar-section">
          <h3>Categories</h3>
          <ul>
            {dummyCategories.map((cat, i) => (
              <li key={i}>
                <a href={`/category/${cat.toLowerCase()}`}>{cat}</a>
              </li>
            ))}
          </ul>
        </section>
      </aside> */}
    </div>
  );
};

export default CategoryPage;
