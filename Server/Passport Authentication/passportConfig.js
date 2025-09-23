import passport from "passport"
import { Strategy as LocalStrategy } from "passport-local"
import { connection } from "../Database Module/Database Connection/databaseConnect.js"

passport.use(new LocalStrategy(async (username,password,done)=>{
    try {
        if(username.trim()=="" || password.trim()==""){
            return done(null,false,{message:"username or password empty"})
        }
        const [rows] = await connection.query(`SELECT * FROM users WHERE name = ?`,[username]);
        if (!rows[0]){
            return done(null,false,{message:"user not found"})
        }
        if(rows[0]){
            if(rows[0].password ===  password){
                return done(null,rows[0])
            }
        }
    } catch (error) {
        return done(error)
    }
}))

passport.serializeUser((user, done) => {
    done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
    try {
        const [rows] = await connection.query('SELECT * FROM users WHERE id = ?', [id]);
        if(rows.length===0){
            done( new Error("User Not Found") );
        }
        const user = rows;
        done(null, user);
    } catch (err) {
        done(err);
    }
});

export default passport