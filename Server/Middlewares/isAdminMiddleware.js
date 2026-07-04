import { DomainError } from "../Domain Errors/domainErrors.js";
import { connection } from "../Database Module/Database Connection/databaseConnect.js";

export const isAdminMiddleware= async (req,res,next)=>{
    try {
        if(!req.user){
            throw DomainError.invalid("Unauthorised User Alert")
        }
        if(req.user.account_type === "ADMIN"){
            next()
        }
        else{
            throw DomainError.invalid("Access Denied...")
        }

    } catch (error) {
        console.error(error)
        throw error
    }
}