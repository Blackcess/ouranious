import { useContext, useEffect, useState } from "react"
import "./Navigation.css"
import { ScreenData } from "../Parent Page/ParentComponent"
import styled from "styled-components"
import { CiMenuBurger } from "react-icons/ci";
import { IoMdClose } from "react-icons/io";
import { NavLink } from "react-router-dom";
import axios from "axios";


const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
function Navigation(){
    const screenData= useContext(ScreenData)
    const [smallScreen,setSmallScreen] = useState(false)


    
    useEffect(()=>{
        setSmallScreen(screenData.screenWidth<=700)
    },[screenData.screenWidth])
    
    
    return <>
    <section className="nav-template">
        <div className={`brand-details ${smallScreen ? "mobile" : ""}`}>
            <div className="brand-logo"></div>
            {(!smallScreen) && <div className="nav-mission">
                <h4>News Online</h4>
            </div>}
        </div>
        
        <div className="module-pages"> 
            <PagesDisplay value={{screenData}}/>
        </div>
    </section>
    </>
}

const BrandTitle = styled.div`
     
`

function PagesDisplay({value}){


    const myPages = ["Home","Categories","Innovation",'App Review',"About","Contact"]
    const myLinks = ["home","home","innovation","app-review","about","contact"]
    const myMobileLinks = ["home","mobile/category","innovation","app-review","about","contact"]
    // const allCategories=["Tech","Business","Entertainment","Health","Science","Sports","World"]
    const [smallScreen,setSmallScreen] = useState(false)
    const [menuSelect,setMenuSelect] = useState(false)
    const [showCategories, setShowCategories] = useState(false);
    const [allCategories,setAllCategories] = useState([])
    const [categoriesLoaded,setCategoriesLoaded] = useState(false)
    useEffect(()=>{
        setSmallScreen(value.screenData.screenWidth<=700)
    },[value.screenData.screenWidth])
    useEffect(()=>{
        value.screenData.feedBack(menuSelect)
        // console.log("The Value Value is ",value)
    },[menuSelect])

    
    useEffect(()=>{
        getCategories()
    },[])

    //get categories from the database
    const getCategories= async()=>{
        try {
            const res= await axios.get(`${API_BASE_URL}/category`,{
                withCredentials:true
            })
            if(res.data.status){
                console.log("Categories are: ",res.data);
                setAllCategories(res.data.data)
                setCategoriesLoaded(true)
            }

        } catch (error) {
            console.error(error )
            setCategoriesLoaded(false)
        }
    }

    const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setShowCategories((prev) => !prev);
    } else if (e.key === "Escape") {
      setShowCategories(false);
    }
  };

    return<>
    <section className="pages-display-template">
       {(!smallScreen) ?
        <ul className="my-pages-list">
      {myPages.map((page, index) => {
        const isCategories = page === "Categories";

        return (
          <li 
            key={index * 100} 
            className="my-pages-list-item"
            onMouseEnter={() => isCategories && setShowCategories(true)}
            onMouseLeave={() => isCategories && setShowCategories(false)}
          >
            <NavLink 
              className={({ isActive }) => 
                isCategories ? "categories-nav-link" : isActive ? "my-pages-list-li-active" : "my-pages-list-li"
              } 
              to={myLinks[index]}
              tabIndex={0}
              onKeyDown={isCategories ? handleKeyDown : undefined}
              aria-haspopup={isCategories ? "true" : undefined}
              aria-expanded={isCategories ? showCategories : undefined}
            >
              {page}
            </NavLink>

            {isCategories && showCategories && (
              <div className="categories-dropdown">
                {allCategories.map((cat, i) => (
                  <NavLink key={i} to={`category?categoryId=${cat.category_id}&categoryName=${cat.name}`} className="dropdown-item"
                  tabIndex={showCategories ? 0 : -1} >
                    {cat.name}
                  </NavLink>
                ))}
              </div>
            )}
          </li>
        );
      })}
    </ul>
        :
        <div className="my-page-list-mobile">
            
            <span><CiMenuBurger 
                style={{fontSize:"18px",fontWeight:"600"}}
                onClick={()=>{
                    setMenuSelect(!menuSelect)
                    }}/>
            </span>
            {(menuSelect) &&<div className="menu-pop-up-nav">
                <div className="menu-close-nav">
                    <IoMdClose onClick={()=>{setMenuSelect(false)}}/>

                </div>
                <ul className="my-pages-list mobile">
                {
                    myPages.map((page,index)=>{
                        return <NavLink key={index*444} className={({isActive})=>{
                            return isActive ? "my-pages-list-li-active-mobile" : "my-pages-list-li-mobile"
                        }} to={`${myMobileLinks[index]}`}
                        onClick={()=>{setMenuSelect(false)}}>{page}</NavLink>
                    })
                }
                </ul>
            </div>
            }
        </div>
        }
    </section>
    </>
}

export default Navigation