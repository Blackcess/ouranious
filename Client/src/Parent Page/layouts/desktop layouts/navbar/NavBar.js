import { useEffect, useState } from "react"
import { useAuth } from "../../../../Recquire Authentication/useAuth"
import "./NavBar.css"
import { CgProfile } from "react-icons/cg";
import { CgLogOut } from "react-icons/cg";
import {logout} from "../../../../Recquire Authentication/APIs/authenticationAPIs"
import { NavLink, useNavigate } from "react-router-dom";
import imageLogo from "./ouranious-logo.jpg"
import styled from "styled-components";


export function DesktopParentNavBar(){
    const [loggingout,setLoggingOut] = useState(false)
    const {authenticated} = useAuth()
    const navigate = useNavigate()

    return <>
    <main className="p-n-template">
        <section className="desktop-parent-nav">
            <div className="org-brand">
                <NavLogo/>
                <h2>
                    <NavLink to={"/home"} style={{textDecoration:"none", color:"white"}}>Ouranious</NavLink>
                </h2>
            </div>

            
            <AppNavigation authenticated={authenticated} />

            {!authenticated ? <span className="nav-get-started">
                <NavLink 
                    className="user-sign-up-in"
                    to={"/login"}
                >
                    sign in
                </NavLink>
                <NavLink 
                    className="user-sign-up-in"
                    to={"/create_account"}
                >
                    register
                </NavLink>
            </span>
            :
            <span className="nav-get-started">
                <button className="user-sign-up-in">
                    <span className="profile-icon"><CgProfile/></span>
                    <span className="profile-text">Profile</span>
                </button>
                <button className="user-sign-up-in">
                    <span className="profile-icon"><CgLogOut/></span>
                    <span className="profile-text" onClick={async ()=>{
                        try{
                            setLoggingOut(true)
                            const response = await logout()
                            if(response.status){
                                navigate("/login",{
                                    state:{from:"/home"},
                                    replace:true
                                })
                            }
                        }
                        catch(error){
                            console.error("Error during logout: ",error)
                        }
                        finally{
                            setLoggingOut(false)
                        }
                    }}>{loggingout ? "logging out..." : "log out"}</span>
                </button>
            </span>
            }
        </section>
    </main>
    </>
}



const AppNavigation = ({authenticated})=>{
    const links = [
        {
            title:"Home",
            link:"/home"
        },
        {
            title:"About Us",
            link:"/about"
        }
    ]

    const authenticatedLinks = [...links]
    if (authenticated) {
        authenticatedLinks.push(
            {
                title:"Community",
                link:"/community"
            },
        )
    }
    return <>
        <ul className="first-grp-nav">
            {
                authenticatedLinks.map((link,index)=>{
                    return  <li>
                                <NavLink to={link.link} style={{color:"white", textDecoration:"none"}}>{link.title}</NavLink>
                            </li>
                })
            }
        </ul>
    </>
}

const NavLogo = styled.div`
    width: 40px;
    height: 40px;
    background: url(${imageLogo}) no-repeat;
    background-position: center;
    background-size: cover;
    border-radius: 50%;
`