import { DomainError } from "../Domain Errors/domainErrors.js";
import { connection } from "../Database Module/Database Connection/databaseConnect.js";


async function authenticationMiddleware(req, res, next) {
    try {
        if(req.user){
            next();
        }
        else{
            throw DomainError.invalid("Authentication Error: User not authenticated", 401);
        }
    } catch (error) {
        console.error("Authentication Middleware Error: ", error);
        if (error instanceof DomainError) {
            res.status(error.status).json({ status: false, message: error.message });
        } else {
            res.status(500).json({ status: false, message: "Internal Server Error" });
        }
    }
}
export {authenticationMiddleware};