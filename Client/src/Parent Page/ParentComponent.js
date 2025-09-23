import { createContext, useEffect, useState } from "react"
import "./ParentComponent.css"
import Navigation from "../Navigation/Navigation"
import { Outlet } from "react-router-dom"


export const ScreenData = createContext()
function ParentComponent(){
    const [screenWidth,setScreenWidth] = useState(0)
    const [parentState,setParentState] = useState("")
    const [menuInitialised,setMenuInitialised] = useState(false)
    useEffect(()=>{
        setScreenWidth(window.innerWidth)
    },[])
    // resizing wevent handling
    useEffect(()=>{
        window.addEventListener("resize",(e)=>{
            setScreenWidth(window.innerWidth)
        })
    },[window.innerWidth])
    useEffect(()=>{
        if(screenWidth<=700){
            setParentState("parent-component-template-small")
        }
        else{
            setParentState("parent-component-template-large")
        }
    },[screenWidth])
    const getMenuStatusFromNav= (status)=>{
        setMenuInitialised(status)
    }
    return <>
    <section className={ `${(menuInitialised) ? `${parentState} disabled` : parentState}`} onClick={()=>{setMenuInitialised(false)}}>
        <div className="nav-bar-section">
            <ScreenData.Provider value={{screenWidth,feedBack:getMenuStatusFromNav}}>
                <Navigation/>
            </ScreenData.Provider>
            
        </div>
        <div className="main-body-section">
            <ScreenData.Provider value={{screenWidth}}>
                <Outlet/>
            </ScreenData.Provider>
            
        </div>
    </section>
    </>
}

export default  ParentComponent