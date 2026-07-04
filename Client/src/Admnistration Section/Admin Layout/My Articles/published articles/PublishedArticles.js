import "./PublishedArticles.css"
import { deletePublishedArticle, getMyPublishedContent } from "../../../APIs/adminAPIs"
import { useEffect, useState } from "react"
import { toast } from "react-toastify"
import SpinLoader from "../../../../Util Components/SpinLoader/SpinLoader"
import { AdminArticleCard } from "./AdminArticleCard"
import { useNavigate } from "react-router-dom"


export function PublishedArticles(){

    const [articles,setArticles] = useState(null)
    const [loading, setLoading] = useState(false)
    const navigation = useNavigate()


    useEffect(()=>{
        load()
    },[])

    const load = async ()=>{
        try {
            setLoading(true)
            const res = await getMyPublishedContent()
            setArticles(res)
        } catch (error) {
            console.error("Error loading published articles ", error)
            toast.error("Error loading articles")
        }
        finally{
            setLoading(false)
        }
    }

    const handleDelete = async (id)=>{
        const res = await deletePublishedArticle(id)
        if(res.status){
            toast.success("Deleted Successfully")
            await load()
        }
        else{
            toast.error("Error occured deleting article")
        }
    }

    if(loading){
        return (
            <>
                <section className="loading-tem">
                    <SpinLoader/>
                </section>
            </>
        )
    }

    
    if(articles !==  null){
        if(articles.length){
            return (
                <>
                    <section className="published-articles-template">
                        {
                            articles.map((article, index)=>{
                                return (
                                    <AdminArticleCard
                                        article={article}
                                        onDelete = {handleDelete}
                                        type="published"
                                    />
                                )
                            })
                        }
                    </section>
                </>
            )
        }
        else{
            return(
                <section className="loading-tem">
                    <h4 className="add-articles-admin">
                        No Published Articles Yet
                    </h4>
                    <p
                        onClick={()=>{
                            navigation("/uploads")
                        }}
                    >Start writing on Ouranious</p>
                </section>
            )
        }
    }
}