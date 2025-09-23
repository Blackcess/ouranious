import { NavLink } from "react-router-dom"
import "./CreateAccountDone.css"

function CreateAccountDone(){
    return <>
    <section className="account-created-section">
        <div className="account-created-container">
            <h1>Account Created Successfully!</h1>
            <p>Your account has been created. You can now log in using your credentials.</p>
            <NavLink to={"/login"}>
                <button className="login-button-redirect">Go to Login</button>   
            </NavLink>
        </div>
    </section>
    </>
}
export default CreateAccountDone;