import { useEffect,useState } from "react";
import axios from "axios";
import { useNavigate,useLocation } from "react-router-dom";



const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
function RecquireAuth({children}){
    const navigate = useNavigate();
    const location = useLocation();
    const [loading,setLoading] = useState(true);
    const [authenticated,setAuthenticated] = useState(false);
    useEffect(()=>{
        const checkAuth = async()=>{
            try {
                const response = await axios.get(`${API_BASE_URL}/test`,{withCredentials:true});
                console.log("Here is my response",response)
                if(response.data.status){
                    console.log("User is Authenticated")
                    setAuthenticated(true);
                    // allow the user to access the protected route
                }
                else{
                    setAuthenticated(false);
                }
            } catch (error) {
                console.error("Error in authentication:..",error);
                setAuthenticated(false);
            }
            finally{
                setLoading(false);
            }
        }
        checkAuth();
    },[])

    if(loading){
        return <div>Loading...</div>
    }
    if(!authenticated){
        navigate("/login",{state:{from:location},replace:true})
        return null;
    }

    return children;
}
export default RecquireAuth;