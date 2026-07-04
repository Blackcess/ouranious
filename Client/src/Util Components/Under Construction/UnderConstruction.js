import "./UnderConstruction.css"
import { LuConstruction } from "react-icons/lu";
function UnderConstruction(){


    return<>
    <section className="construction-template">
    <div className="construction-body">
        <div className="under-construction-image-banner"></div>
        <p className="construction-alert-poster">
            {/* <span><LuConstruction/></span> */}
            <span className="construction-alert-text">Under Construction</span>
        </p>
    </div>
    </section>
    </>
}

export default UnderConstruction