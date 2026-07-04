import passport from "passport";
import { Strategy as GoogleStrategy } from "passport-google-oauth20";
import { connection } from "../Database Module/Database Connection/databaseConnect.js";

passport.use(new GoogleStrategy(
{
    clientID: process.env.Google_client_id,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: "/auth/google/callback"
},
async (accessToken, refreshToken, profile, done) => {
    try {
        const googleId = profile.id;
        const email = profile.emails?.[0]?.value;
        const name = profile.displayName;

        // 1️⃣ already registered via google
        const [gRows] = await connection.query(
            `SELECT * FROM users WHERE google_id = ?`,
            [googleId]
        );

        if (gRows.length) {
            return done(null, gRows[0]);
        }

        // 2️⃣ existing local account with same email → link
        const [emailRows] = await connection.query(
            `SELECT * FROM users WHERE email = ?`,
            [email]
        );

        if (emailRows.length) {
            await connection.query(
                `UPDATE users 
                 SET google_id = ?, auth_provider = 'google'
                 WHERE id = ?`,
                [googleId, emailRows[0].id]
            );

            return done(null, emailRows[0]);
        }

        // 3️⃣ new google user
        const [insertResult] = await connection.query(
            `INSERT INTO users (create_time, email, google_id, username, account_type, auth_provider)
             VALUES (NOW(), ?, ?, ?, 'USER', 'google')`,
            [email, googleId, name]
        );

        const [newUser] = await connection.query(
            `SELECT * FROM users WHERE id = ?`,
            [insertResult.insertId]
        );

        return done(null, newUser[0]);

    } catch (err) {
        return done(err, null);
    }
}));