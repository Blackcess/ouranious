import { FaTag } from "react-icons/fa6";
import "./MobileNavigation.css"
import { NavLink } from "react-router-dom";
export function MobileNavigation(){
    const titles = ["Uploads","Home","Profile"]
    const icons = [<FaTag/>,<FaTag/>,<FaTag/>]
    const paths=["/admin/uploads","/home","/home"]
    return <>
        <section className="mob-na-temp">
            {
                titles.map((t,index)=>{
                    return <NavEntity icon={icons[index]} title={t} path={paths[index]}/>
                })
            }
        </section>
    </>
}

function NavEntity({icon,title,path}){

    return <>
        <NavLink className="nav-entity-mob-na" to={`${path}`}>
            <span className="nav-entity-tag-77 icon">{icon}</span>
            <span className="nav-entity-tag-77 title">{title}</span>
        </NavLink>
    </>
}