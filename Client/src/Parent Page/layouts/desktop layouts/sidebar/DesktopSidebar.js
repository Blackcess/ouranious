import { useState, useEffect} from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "./DesktopSideBar.css"
import { useAuth } from "../../../../Recquire Authentication/useAuth";

export function DesktopSidebar(){

    const [sidebarOpen, setSidebarOpen] = useState(false); // mobile sidebar
    const [collapsed, setCollapsed] = useState(false); // desktop collapse
    const navigate = useNavigate()
    const sessionData = useAuth()
    
    return <>
        <section className="sidebar-xtx">
            <aside className={`sidebar ${collapsed ? "collapsed" : ""} `}>
                <NavLink className="logo" to={"/landing"}>{collapsed ? "O" : "Ouranious"}</NavLink>
                <nav className="nav-links-sidebar">
                    <NavLink to="/home" >
                        <i className="fas fa-tachometer-alt"></i>
                        {!collapsed && "Home"}
                    </NavLink>
                    <NavLink to="/article/news" >
                        <i className="fas fa-newspaper"></i>
                        {!collapsed && " Articles"}
                    </NavLink>
                    {(sessionData.authenticated && sessionData.user.account_type=="ADMIN")&&<NavLink to="/admin/uploads" >
                        <i className="fas fa-upload"></i>
                        {!collapsed && " Upload"}
                    </NavLink>}
                    <NavLink to="users" >
                        <i className="fas fa-users"></i>
                        {!collapsed && " Users"}
                    </NavLink>
                    <NavLink to="settings" >
                        <i className="fas fa-cog"></i>
                        {!collapsed && " Settings"}
                    </NavLink>
                </nav>

                {/* Collapse toggle (desktop only) */}
                <button
                    className="collapse-btn"
                    onClick={() => setCollapsed(!collapsed)}
                >
                    <i className={`fas ${collapsed ? "fa-angle-right" : "fa-angle-left"}`}></i>
                </button>
            </aside>
        </section>
    </>
}