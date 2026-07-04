import { app } from "../../src/server.js";
import { checkByUserName,createTraditionalAccount } from "../../Database Module/Login API/loginQueries.js";
import { DomainError } from "../../Domain Errors/domainErrors.js";
import bycrpt from "bcrypt";
import { Router } from "express";
import passport from "../../Passport Authentication/passport.index.js";
import { isOnboardingCompleted } from "../../Passport Authentication/utilities/onbordingUtilities.js";

export const authenticationRouter = Router();
authenticationRouter.get("/google",
    passport.authenticate("google", { scope: ["profile", "email"] })
);
authenticationRouter.get(
  "/google/callback",
  (req, res, next) => {
    passport.authenticate("google", async (err, user, info) => {
      if (err) return next(err);
      if (!user) {
        return res.redirect(`${process.env.LOCALHOST_CLIENT_URL}/login`);
      }

      // log the user into session
      req.logIn(user, (err) => {
        if (err) return next(err);

        // 🔥 your custom redirect logic
        if (isOnboardingCompleted(user)) {
          return res.redirect(`${process.env.LOCALHOST_CLIENT_URL}/home`);
        } else {
          return res.redirect(`${process.env.LOCALHOST_CLIENT_URL}/onboarding`);
        }
      });
    })(req, res, next);
  }
);


const test= async(req,res)=>{
    if(req.user){
        res.status(200).json({
            status:true,
            msg:req.isAuthenticated(),
            user:req.user
        })
    }
    else{
        res.status(200).json({status:false,msg:"user not authenticated"})
    }    
}

authenticationRouter.get("/test",test)
const login = async (req,res)=>{
    try {
        //email/username and password are passed to this route via query strings...
        const {username,password} = req.body;
        if(!(username && password)){
            throw DomainError.invalid("Invalid Credentials")
        }
        //for the sake of cleanliness I will define the function that communicartes with the database externally...
        const result = await checkByUserName(username);
        // console.log("Sending Welcome Gift To ",result[0].name)
        res.status(200).json({msg:"Success"})
       

    } catch (error) {
        console.error("Error in logging in:..",error);
        throw error;
        // res.status(500).json({msg:"Bad Request",error:error.message})
    }
}

// create a route that will determine in which group the user is, if he/she is even logged in
const checkAccountType = async (req,res)=>{
    if(req.isAuthenticated() && req.user){
        res.status(200).json({account_type:req.user})
    }
    else{
        throw DomainError.invalid("User Not Authenticated")
    }
}


const  createTraditionalAccount_Route =async (req,res)=>{
        try {
            const {email,password,username,account_type} = req.body;
            if(!(email && password && username)){
                throw DomainError.invalid("Invalid Credentials")
            }
            await createTraditionalAccount(email,password,username,account_type);
            res.status(200).json({status:true})
        } catch (error) {
            console.error(error);
            throw error;
            // res.status(500).json({status:false,error:error.message})
        }
}  

export {test,login,createTraditionalAccount_Route,checkAccountType}

