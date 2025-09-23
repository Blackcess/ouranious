import session from "express-session";
import  MySqlStoreFactory from "express-mysql-session"
import dotenv from "dotenv"

dotenv.config();

const MySqlStore = MySqlStoreFactory(session);
const sessionStore = new MySqlStore({
    host: process.env.DATABASE_HOST,
    user: process.env.DATABASE_USERNAME,
    password: process.env.DATABASE_PASSWORD,
    database: process.env.DATABASE_NAME
})
export const sessionMiddleware = session({
    secret: 'your_secret_key',
    resave: false,
    saveUninitialized: false,
    store: sessionStore,
    cookie:{
        maxAge: 1000 * 60 * 60 * 24 * 30 // 30 days
    }
});