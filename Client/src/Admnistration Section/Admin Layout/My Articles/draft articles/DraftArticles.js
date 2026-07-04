import { useEffect, useState } from "react"
import "./DraftArticles.css"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import { getAuthorDrafts, deleteDraftArticle} from "../../../APIs/adminAPIs"
import SpinLoader from "../../../../Util Components/SpinLoader/SpinLoader"
import {AdminArticleCard} from "../published articles/AdminArticleCard"

export function DraftArticles() {


    const [articles,setArticles] = useState(null)
    const [loading, setLoading] = useState(false)

    const navigation = useNavigate()

    useEffect(()=>{
        load()
    },[])
    
    const load = async ()=>{
        try {
            setLoading(true)
            const res = await getAuthorDrafts()
            setArticles(res)
        } catch (error) {
            console.error("Error loading draft articles ", error)
            toast.error("Error loading draft articles")
        }
        finally{
            setLoading(false)
        }
    }

    const handleDelete = async (id)=>{
        const res = await deleteDraftArticle(id)
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
                                        type="draft"
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
                        No Draft Articles Yet
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