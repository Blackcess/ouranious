import { useState } from "react"
import { getRecommemendedHomeAricles } from "../Apis/homepageApis"
import { useEffect } from "react"
import SpinLoader from "../../Util Components/SpinLoader/SpinLoader"
import { ArticleCard } from "../../Content Management/Articles/Content Documents Style/article card/ArticleCard"


function LatestArticle(){

    const [articles, setArticles]= useState(null)
    const [loading,setLoading] = useState(false)

    useEffect(()=>{
        async function load(){
            try {
                setLoading(true)
                setArticles(await getRecommemendedHomeAricles())
            } catch (error) {
                console.error("Error fetching home recommended ",error)
            }
            finally{
                setLoading(false)
            }
        }

        load()
    },[])

    if(loading){
        <div className="home-loader">
            <SpinLoader/>
        </div>
    }
    return (
        <>
            <section className="latest-article-template">
                {
                    (articles) ? articles.map((article, index)=>{
                        return <ArticleCard article={article} key={index}/>
                    })
                    :
                    <p>No Articles Recorded</p>
                }
            </section>
        </>
    )
}


export default LatestArticle