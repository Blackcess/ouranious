import "./CreateAccount.css"
import "../Login/Login.css"
import axios from "axios";
import { useState,useEffect} from "react";
import { NavLink, useNavigate } from "react-router-dom";
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function CreateAccount(){
    const [step,setStep]= useState(1);
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const [confirmPassword,setConfirmPassword] = useState("");
    const [accountType, setAccountType] = useState('USER');
    const [errorMessages, setErrorMessages] = useState([]);
    const navigate = useNavigate();
    const handleSubmit = async(e)=>{
        e.preventDefault();
        try {
            if(password !== confirmPassword){
                throw new Error("Passwords do not match");
            }
            const response = await axios.post(`${API_BASE_URL}/create_account/traditional`,{
                username:email,
                password,
                account_type:accountType
            },{withCredentials:true});
            console.log("Account Creation Response ",response)
            if(response.data.msg===true){
                navigate("/create-account-done");
            }
            
            
        } catch (error) {
            console.error("Error during creating account:..",error)
            pushError(error.response?.data?.msg ||error?.response?.data?.error|| error.message + ". Try again later");
            // setErrorMessages(prevMessages => [...prevMessages, error.message]);
        }
    }
      const handleChange = (e) => {
    setAccountType(e.target.value);
  };
  useEffect(()=>{
    console.log("My error queue is: ",errorMessages)
  },[errorMessages])
  const pushError =(msg)=>{
    setErrorMessages(prevMessages =>{
        // if(prevMessages.includes(msg)){
        //     return prevMessages; // Avoid adding duplicate messages
        // }
        return [msg];
    } );
  }
    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleSubmit}>
                <div className="step-analyser">
                    <div className={`step ${step>=1 ? "active-step":""}`} onClick={(e)=>{
                        e.preventDefault();
                        setStep(1);
                    }}></div>
                    <div className={`step ${step===2 ? "active-step":""}`}></div>
                </div>
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
                </>}
    {(step===2) &&<div className="form-group">
      <p>Select Account Type:</p>
      <label>
        <input
          type="radio"
          name="enumOption"
          value="ADMIN"
          checked={accountType === 'ADMIN'}
          onChange={handleChange}
          disabled={true}
        />
        Admin
      </label>
      <label>
        <input
          type="radio"
          name="enumOption"
          value="CREATOR"
          checked={accountType === 'CREATOR'}
          onChange={handleChange}
          disabled={true}
        />
        Content Creator
      </label>
      <label>
        <input
          type="radio"
          name="enumOption"
          value="USER"
          checked={accountType === 'USER'}
          onChange={handleChange}
        />
        User
      </label>
    </div>
    }
        {
           (step===1) ? <button className="login-button" onClick={(e)=>{
                e.preventDefault();
                if(!(email && password && confirmPassword)){
                    pushError("Please fill in all fields");
                    return;
                }
                if(password !== confirmPassword){
                    pushError("Passwords do not match");
                    return;
                }
                // if(errorMessages.length > 0) {
                //     return; // Prevent moving to next step if there are errors
                // }
                if(email.includes("@")===false){
                    pushError("Please enter a valid email address");
                    return;
                }
                setErrorMessages([])
                setStep(2);
           }}>Next</button>
           :  <button type="submit" className="login-button">Sign Up</button>
        }
        <div className="error-collection">
            {errorMessages.map((msg, index) => (
                <p key={index} className="error-message">{msg}</p>
            ))}
        </div>
        <NavLink to={"/login"}>
        <p className="create-account-link">Already have an account? Login</p>       
    </NavLink>
    </form>
    
        </div>
    )
}
export default CreateAccount;