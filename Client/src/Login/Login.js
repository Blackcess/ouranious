import "./Login.css"
import axios from "axios";
import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import styled from "styled-components";
import logoImg from "./ouranious-logo.jpg";
import { FcGoogle } from "react-icons/fc";
import { RightLogPanel } from "../Account Creation/CreateAccount";
import {login, checkAuthentication} from "../Recquire Authentication/APIs/authenticationAPIs"
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;


function Login(){
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const navigate = useNavigate()
    const handleSubmit = async(e)=>{
        e.preventDefault();
        try {
            const response = await login(email,password)

            navigate("/home",{
                state:{from:"/login"},
                replace:true
            });
        } catch (error) {
            console.error("Error during login:..",error)
        }
    }
    const checkAuthenticationStatus = async ()=>{
        try {
            const response= await checkAuthentication()
            if(response.status){
                navigate("/home")
            }
        } catch (error) {
            console.error("Error checking authentication status: ",error)
        }
    }
    useEffect(()=>{
        checkAuthenticationStatus()
    },[])
    return (
        <div className="login-container">
            <form className="login-form" >
                <div className="form-left">
                    {/* <div className="business-logo"></div> */}
                    <StyledLogo ></StyledLogo>
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
                    <div className="or-divider">or</div>
                    <button className="google-login-button" onClick={
                        async()=>{
                            window.location.href = `${process.env.REACT_APP_API_BASE_URL}/auth/google`;
                        }}
                    >
                        
                        <FcGoogle  />
                        <span style={{marginLeft:"8px"}}>Login with Google</span>
                    </button>
                    <NavLink to={"/create_account"}>
                        <p className="create-account-link">Don't have an account? Create one</p>
                    </NavLink>
                </div>
                <div className="form-right">
                    <RightLogPanel/>
                </div>
                
            </form>
        </div>
    )
}
const StyledLogo = styled.div`
    width: 50px;
    height: 50px;
    background: url(${logoImg}) no-repeat;
    background-position: center;
    background-size: cover;
    border-radius: 50%;
    margin-left: auto;
    margin-right: auto;
`


export { StyledLogo, Login };