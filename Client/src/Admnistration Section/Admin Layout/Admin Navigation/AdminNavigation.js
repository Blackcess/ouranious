import { NavLink } from "react-router-dom";
import "./AdminNavigation.css"
import { IoMdCreate } from "react-icons/io";


export function AdminNavigation(){
    const navItems = [
        {
            title: "create",
            link: "",
            icon: <IoMdCreate/>
        }
       
    ]

    return (
        <>
            <section className="admin-nav">
                <ul>
                    {
                        navItems.map((item, key)=>{
                            return (
                                <li key={key}>
                                    <NavLink 
                                        className={"admin-nav-linjks"}
                                        to={`/uploads`}
                                    >
                                        {item.icon}
                                        {item.title}
                                    </NavLink>
                                    
                                </li>
                            ) 
                        })
                    }
                </ul>
            </section>
        </>
    )
}