import { createContext, useEffect,useState } from "react";
import axios from "axios";
import { useNavigate,useLocation } from "react-router-dom";
import { checkAuthentication } from "./APIs/authenticationAPIs";
import AuthContext from "./authContext";
import SpinLoader from "../Util Components/SpinLoader/SpinLoader";
import "./RecquireAuth.css"


const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
function RecquireAuth({children}){
    const navigate = useNavigate();
    const location = useLocation();
    const [loading,setLoading] = useState(true);
    const [authenticated,setAuthenticated] = useState(false);
    const [user,setUser] = useState(null)
    useEffect(() => {
    const initAuth = async () => {
      try {
        const response = await checkAuthentication()
        if (response.status) {
          setAuthenticated(true);
          setUser(response.user ?? null); // if backend sends user
        } else {
          setAuthenticated(false);
          setUser(null);
        }
      } catch (err) {
        console.error("Auth init failed:", err);
        setAuthenticated(false);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

    const value = {
    authenticated,
    loading,
    user,
    setAuthenticated, // useful for login/logout
    setUser,
  };

  if(loading){
    return <div className="checking-authentication">
        <div className="c-a-template">
          <span>Ouranious Is  Checking Authentication...</span>
          <span><SpinLoader/></span>
        </div>
    </div>
  }

  return (
      <AuthContext.Provider value={value}>
          {children}
      </AuthContext.Provider>
  );
}

export default RecquireAuth;