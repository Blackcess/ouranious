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
    cookie: {
    httpOnly: true,            // not accessible via JS
    secure: false,             // must be false for HTTP (LAN/testing)
    sameSite: "lax",           // allows cross-origin requests from your LAN/dev frontend
    maxAge: 24 * 60 * 60 * 1000 // optional: cookie expires in 1 day
  }
});