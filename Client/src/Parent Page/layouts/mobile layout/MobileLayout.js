import { Outlet, useNavigate } from "react-router-dom"
import { MobileNavigation } from "./mobile navigation/MobileNavigation"
import "./MobileLayout.css"
import { useEffect } from "react"
import { DesktopParentNavBar } from "../desktop layouts/navbar/NavBar"

export function MobileLayout({screenWidth}){
    const navigate = useNavigate()
    return <>
        <section className="mobile-template">
            <div className="mobile-main-area">
                {/* <DesktopParentNavBar/> */}
                <Outlet/>
            </div>
            {/* <MobileNavigation/> */}
        </section>
    </>
}