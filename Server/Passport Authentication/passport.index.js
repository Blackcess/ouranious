import passport from "passport";
import "./passport.local.js";
import "./passport.google.js";
import { connection } from "../Database Module/Database Connection/databaseConnect.js";
import { DomainError } from "../Domain Errors/domainErrors.js";

passport.serializeUser((user, done) => {
    done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
    try {
        const [rows] = await connection.query('SELECT * FROM users WHERE id = ?', [id]);
        if(rows.length===0){
            done( DomainError.notFound("USER_NOT_FOUND") );
        }
        const user = rows;
        console.log("The user is ", user[0]);
        done(null, user[0]);
    } catch (err) {
        done(err);
    }
});
export default passport;