import { useContext, useEffect, useState } from "react";
import "./Home.css"
import { useNavigate } from "react-router-dom";
import { ScreenData } from "../Parent Page/ParentComponent";
import styled from "styled-components";
import NewsCard from "../Content Management/Articles/NewsCard";

function Home(){
    const navigate = useNavigate();
    const screenData = useContext(ScreenData)
    const [smallScreen,setSmallScreen] = useState(screenData.screenWidth<=700)
    const displayingPages= ["App Review","Budgets","Innovation"]
    const headings= ["Bently Smart Chip Hits One Million Users",
                     "2035 Best AR Apps for iPad",
                     "Dwell Announces a New Streaming Service"
    ]
    const articleBodies=["Double click what you want to edit and then select 'Change Content' to add your own content to the collection."]
    const backgroundImages = ["https://static.wixstatic.com/media/84770f_aa3e526ff51b4f25956d57ea0a3a772e~mv2_d_4000_2020_s_2.jpg/v1/fill/w_1047,h_430,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/84770f_aa3e526ff51b4f25956d57ea0a3a772e~mv2_d_4000_2020_s_2.jpg",
                               "https://static.wixstatic.com/media/84770f_d7022dca00f54ed2a7945540f6698ab2~mv2_d_4000_2667_s_4_2.jpg/v1/fill/w_524,h_562,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/84770f_d7022dca00f54ed2a7945540f6698ab2~mv2_d_4000_2667_s_4_2.jpg",
                               "https://static.wixstatic.com/media/84770f_e46c5dc9395c46acbe5569e523a04203~mv2_d_3948_2986_s_4_2.jpg/v1/fill/w_524,h_562,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/84770f_e46c5dc9395c46acbe5569e523a04203~mv2_d_3948_2986_s_4_2.jpg"
    ]

    useEffect(()=>{
        
        if(screenData.screenWidth<=700){
            setSmallScreen(true)
        }
        else{
            setSmallScreen(false)
        }
    },[screenData.screenWidth])
    useEffect(()=>{
        console.log("Screen Size Is ",screenData.screenWidth,smallScreen)
    },[screenData.screenWidth])
    

    return (
        <section className="home-container">
            <div className={`home-exhibit-a ${(smallScreen)? "mobile": ""}`}>
                <div className={`home-get-newsletter ${smallScreen ? "mobile" : ""}`}>
                    
                    <NewsLetterRequest value={{smallScreen}}/>
                </div>
                <div className={` ${smallScreen ? "home-pages-review-mobile" : "home-pages-review"}`}>
                    {
                        displayingPages.map((page,index)=>{
                            return <PageReviewTemplate key={index} value={{background:backgroundImages[index],page,heading:headings[index],body:articleBodies[0],smallScreen}}/>
                        })
                    }
                   
                </div>
            </div>
            <div className={`home-exhibit-b ${(smallScreen)? "mobile": ""}`}>
                <div className={`home-latest-articles ${(smallScreen) ? "mobile": ""}`}>
                    <div className="latest-articles-header">
                        <h2 className="latest-articles-head">Latest Articles</h2>
                        <button className="view-all-articles-button" onClick={()=>navigate("/articles")}>View All Articles</button>
                    </div>
                    <div className={`latest-articles-contents ${(smallScreen) ? "mobile": ""}`}>
                        {/* Article Cards */}
                        <NewsCard/>
                        <NewsCard/>
                        <NewsCard/>
                        <NewsCard/>
                    </div>
                </div>
            </div>



        </section>
    )
}

function NewsLetterRequest({value}){
    const [email,setEmail] = useState("")

    return <>
    <section className={`newsletter-request-template ${value.smallScreen ? "mobile": ""}`}>
        <div className="ouranious-prestige">
            <div className="gsgsh">
                <span className="o-p-1">Ouranious</span>
                <span className="o-p-1">Daily News</span>
            </div>
            
            <span className="side-note-o-p">Everything You Need To Know About Tech</span>
        </div>
        <div className="email-request">
            <div className="sub-pliz">Subscribe To Receive The Latest Tech News</div>
            <div className="subscribe-form">
                <form className="form-group-sub">
                    <div className="email-enter">
                         <label htmlFor="email" className="email-label-form">Email *:</label>
                         <input 
                            type="email" 
                            id="email" 
                            value={email} 
                            onChange={(e)=>setEmail(e.target.value)} 
                            recquired
                            placeholder="enter your email"
                        />
                    </div>
                   
                    <div className="newsletter-confirm">
                        <input
                        type="checkbox"
                        recquired
                        />
                        <span>Yes, subscribe me to your newsletter</span>
                    </div>
                    <button className="newsletter-submit-button">Submit</button>
                </form>
            </div>
        </div>
    </section>
    </>
}

function PageReviewTemplate({value}){

    return<>
    <PageReTemp className="page-review-template" value={{background:value.background}}>
        <div className="page-details">
            <div className="page-dets-name">{value.page}</div>
            <div className="page-art-published-data">02/09/2025</div>
        </div>
        <div className="article-details-template">
            <h2 className="art-head">{value.heading}</h2>
            <div className="art-body">
                <p className="article-passage">
                    {value.body}
                </p>
            </div>
        </div>
        <div className="learn-more-template">
            <button className="learn-more-button">Learn More</button>
            
        </div>
    </PageReTemp>
    </>
}
const PageReTemp= styled.section`
    width:auto;
    display: flex;
    flex-shrink:1;
    flex-grow:1;
    flex-direction: column;
    gap: 45px;
    color: white;
    background:linear-gradient(rgba(0, 0, 0, 0.53), rgba(0, 0, 0, 0.645)), url(${(props)=>{return props.value.background}});
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
    padding: 25px;
    border-radius:20px;
`


export default Home;