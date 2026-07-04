import { NavLink, Outlet } from "react-router-dom"
import "./MyArticles.css"

export function MyArticles(){


    return (
        <>
            <section className="my-articles-section">
                <h1 className="my-artixles-header">
                    My Articles
                </h1>

                <div className="my-articles-nav">
                    <ul>
                        <li>
                            <NavLink
                                className={"my-articles-nabvlinks"}
                                to={"/admin/published"}
                            >
                                <h4>
                                    Published
                                </h4>
                            </NavLink>
                            <NavLink
                                className={"my-articles-nabvlinks"}
                                to={"/admin/drafts"}
                            >
                                <h4>
                                    Drafts
                                </h4>
                            </NavLink>
                        </li>
                    </ul>
                </div>

                <Outlet/>

            </section>
        </>
    )
}