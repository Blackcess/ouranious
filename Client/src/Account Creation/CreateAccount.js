import "./CreateAccount.css"
import "../Login/Login.css"
import axios from "axios";
import { useState,useEffect} from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { createTraditionalAccount, checkOnbordingViaEmail } from "./APIs/createAccountAPIs";
import { IoCheckmarkOutline } from "react-icons/io5";
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export function CreateAccount(){
    const [step,setStep]= useState(1);
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const [username,setUsername] = useState("");
    const [confirmPassword,setConfirmPassword] = useState("");
    const [accountType, setAccountType] = useState('USER');
    const [errorMessages, setErrorMessages] = useState([]);
    const navigate = useNavigate();



    const handleSubmitLocal = async(e)=>{
        e.preventDefault();
        try {
            if(password !== confirmPassword){
                throw new Error("Passwords do not match");
            }
            const response = await createTraditionalAccount(email,password,accountType,username);
            if(response){
                // navigate("/create-account-done");
                const onboardingProfile= await checkOnbordingViaEmail(email)
                console.log("My onboarding profile is",onboardingProfile)
            }
        } catch (error) {
            console.error("Error during creating account:..",error)
            pushError(error.response?.data?.message + ". Try again later");
            // setErrorMessages(prevMessages => [...prevMessages, error.message]);
        }
    }
      const handleChange = (e) => {
    setAccountType(e.target.value);
  };
useEffect(()=>{},[errorMessages])
const pushError =(msg)=>{
    setErrorMessages(prevMessages =>{
        return [msg];
    } );
}
    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleSubmitLocal}>
                <div className="form-left">
                            <div className="business-logo"></div>
                            <h2>Create Account</h2>
                            { (step===1) &&
                            <> 
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
                                <label htmlFor="username">Username:</label>
                                <input 
                                    type="text" 
                                    id="username" 
                                    value={username} 
                                    onChange={(e)=>setUsername(e.target.value)} 
                                    required 
                                    placeholder="enter your username"
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
                            <div className="form-group">
                                <label htmlFor="password">Password:</label>
                                <input 
                                    type="password" 
                                    id="password-confirm" 
                                    value={confirmPassword} 
                                    onChange={(e)=>setConfirmPassword(e.target.value)} 
                                    required 
                                    placeholder="Confirm Password"
                                />
                            </div>
                            </>
                        }
                    <button type="submit" className="login-button" onClick={(e)=>{
                            // e.preventDefault();
                            if(!(email && password && confirmPassword)){
                                pushError("Please fill in all fields");
                                return;
                            }
                            if(password !== confirmPassword){
                                pushError("Passwords do not match");
                                return;
                            }
                            if(email.includes("@")===false){
                                pushError("Please enter a valid email address");
                                return;
                            }
                            setErrorMessages([])
                            // setStep(2);
                    }}>Submit</button>
                    <div className="or-divider">or</div>
                    <button className="google-button" onClick={async()=>{
                        window.location.href = `${process.env.REACT_APP_API_BASE_URL}/auth/google`;
                    }}>Continue With Google</button>
                    <div className="error-collection">
                        {errorMessages.map((msg, index) => (
                            <p key={index} className="error-message">{msg}</p>
                        ))}
                    </div>
                    <NavLink to={"/login"}>
                        <p className="create-account-link">Already have an account? Login</p>       
                    </NavLink>
                </div>
                <div className="form-right">
                    <RightLogPanel/>
                </div>
                
    </form>
    
        </div>
    )
}

export function RightLogPanel(){

    const offers=[
        "Access inclusive market insights and reports",
        "Explore resources for startup and enterprenuers",
        "Market your startup and reach your target audience",
        "Enjoy special offers and discounts"
    ];

    return (
        <>
            <h1 className="form-right-title">Accelerate Your Startup With Ouranious</h1>
            <ul className="offer-list">
                {offers.map((offer,index)=>(
                    <li key={index} className="offer-item">
                        <IoCheckmarkOutline className="check-icon"/>
                        {offer}
                    </li>
                ))}
            </ul>
        </>
    )

}

