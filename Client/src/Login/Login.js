import "./Login.css"
import axios from "axios";
import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function Login(){
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const navigate = useNavigate()
    const handleSubmit = async(e)=>{
        e.preventDefault();
        try {
            const response = await axios.post(`${API_BASE_URL}/login`,{
                username:email,
                password
            },{
                withCredentials:true
            });
            console.log("Here is my response after login",response)
            // redirect the user to the home page
            if(response.data.msg){
                navigate("/ourans-platform/home",{
                    state:{from:"/login"},
                    replace:true
                });
            }
        } catch (error) {
            console.error("Error during login:..",error)
        }
    }
    const checkAuthenticationStatus = async ()=>{
        try {
            const response= await axios.get(`${API_BASE_URL}/test`,{
            withCredentials:true
            })
            if(response.data.status){
                navigate("/ourans-platform/home")
            }
        } catch (error) {
            
        }
    }
    useEffect(()=>{
        checkAuthenticationStatus()
    },[])
    return (
        <div className="login-container">
            <form className="login-form" >
                <div className="business-logo"></div>
                <h2>Login</h2>
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input 
                        type="email" 
                        id="email" 
                        value={email} 
                        onChange={(e)=>setEmail(e.target.value)} 
                        required 
                        placeholder="enter your email"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input 
                        type="password" 
                        id="password" 
                        value={password} 
                        onChange={(e)=>setPassword(e.target.value)} 
                        required 
                        placeholder="enter your password"
                    />
                </div>
                <button type="submit" className="login-button" onClick={handleSubmit}>Login</button>
                <NavLink to={"/create_account"}>
                    <p className="create-account-link">Don't have an account? Create one</p>
                </NavLink>
            </form>
        </div>
    )
}

export default Login;