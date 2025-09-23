import { app } from "../src/server.js";
import { checkByUserName,createTraditionalAccount } from "../Database Module/Login API/loginQueries.js";


const test= async(req,res)=>{
    try {
        // console.log("Login Status: ",req.isAuthenticated())
        if(req.isAuthenticated() && req.user){
            res.status(200).json({status:true,msg:req.isAuthenticated()})
        }
        else{
            throw new Error("User Not Authenticated")
        }
        
    } catch (error) {
        console.error("Error in /test route:..",error);
        res.status(500).json({status:false,msg:"Not Authorised",error:error.message})
    }
}
const login = async (req,res)=>{
    try {
        //email/username and password are passed to this route via query strings...
        const {username,password} = req.body;
        if(!(username && password)){
            throw new Error("Invalid Credentials")
        }
        //for the sake of cleanliness I will define the function that communicartes with the database externally...
        const result = await checkByUserName(username);
        console.log("Sending Welcome Gift To ",result[0].name)
        res.status(200).json({msg:"Success"})

    } catch (error) {
        console.error("Error in logging in:..",error);
        res.status(500).json({msg:"Bad Request",error:error.message})
    }
}

// create a route that will determine in which group the user is, if he/she is even logged in
const checkAccountType = async (req,res)=>{
    if(req.isAuthenticated() && req.user){
        res.status(200).json({account_type:req.user})
    }
    else{
        throw new Error("User Not Authenticated")
    }
}


const  createTraditionalAccount_Route =async (req,res)=>{
        try {
            const {username,password,account_type} = req.body;
            if(!(username && password)){
                throw new Error("Invalid Credentials")
            }
            await createTraditionalAccount(username,password,account_type);
            res.status(200).json({msg:true})
        } catch (error) {
            console.error(error);
            res.status(500).json({msg:false,error:error.message})
        }
}  

export {test,login,createTraditionalAccount_Route,checkAccountType}

