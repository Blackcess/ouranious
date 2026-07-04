import { createContext, useContext, useEffect, useState } from "react"
import "./ParentComponent.css"
import Navigation from "../Navigation/Navigation"
import { Outlet } from "react-router-dom"
import { DesktopLayout } from "./layouts/desktop layouts/DesktopLayout"
import { MobileLayout } from "./layouts/mobile layout/MobileLayout"

export const ScreenData = createContext()

function ParentComponent(){
    const [screenWidth,setScreenWidth] = useState(0)
    

    useEffect(()=>{
        setScreenWidth(window.innerWidth)
    },[])
    // resizing wevent handling
    useEffect(()=>{
        window.addEventListener("resize",(e)=>{
            setScreenWidth(window.innerWidth)
        })
    },[window.innerWidth])


    if(screenWidth>=750){
        return <ScreenData.Provider value={{screenWidth}}><DesktopLayout /></ScreenData.Provider>
    }
    else{
        return <ScreenData.Provider value={{screenWidth}}><MobileLayout /></ScreenData.Provider>
    }   
}

export default  ParentComponent

