import { DesktopSidebar } from "./sidebar/DesktopSidebar";
import "./DesktopLayout.css"
import { Outlet, useNavigate } from "react-router-dom";
import { createContext, useContext, useEffect } from "react";
import { DesktopParentNavBar } from "./navbar/NavBar";

export const ScreenData = createContext()
export function DesktopLayout(){
    const navigate = useNavigate()
    
    return <>
        <section className="desktop-main-area">
            <DesktopParentNavBar/>
            <div className="main-outlet">
                <Outlet/>
            </div>
            
        </section>
    </>
}