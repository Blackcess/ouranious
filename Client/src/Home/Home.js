import { useContext, useEffect, useState } from "react";
import "./Home.css"
import { ScreenData } from "../Parent Page/ParentComponent";
import LatestArticle from "./Sub Modules Collection/LatestArticles";



function Home(){
    const [loading,setLoading] = useState(true)
    const screenData = useContext(ScreenData)
    const [smallScreen,setSmallScreen] = useState(screenData.screenWidth<=700)
    

    useEffect(()=>{
        
        if(screenData.screenWidth<=700){
            setSmallScreen(true)
        }
        else{
            setSmallScreen(false)
        }
    },[screenData.screenWidth])

    
    return (
        <section className="home-container">
            <LatestArticle/>
        </section>
    )
}






export default Home;