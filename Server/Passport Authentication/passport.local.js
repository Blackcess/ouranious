import passport from "passport"
import { Strategy as LocalStrategy } from "passport-local"
import { connection } from "../Database Module/Database Connection/databaseConnect.js"
import { DomainError } from "../Domain Errors/domainErrors.js"
import bycrpt from "bcrypt"

passport.use(new LocalStrategy({usernameField:"email",passwordField:"password"},async (email,password,done)=>{
    try {
        if(email.trim()=="" || password.trim()==""){
            return done(null,false,{message:"email or password empty"})
        }
        
        const [rows] = await connection.query(`SELECT * FROM users WHERE email = ?`,[email]);
        if (!rows[0]){
            return done(null,false,{message:"user not found"})
        }
        
         // 🚫 block google accounts from using password login
        if (rows[0].auth_provider === "google") {
            return done(null, false, {
                message: "Use Google login for this account"
            });
        }
        if(rows[0]){
            const isPasswordValid = await bycrpt.compare(password,rows[0].password)
           
            return done(null,rows[0])
        }
    } catch (error) {
        return done(error)
    }
}))



