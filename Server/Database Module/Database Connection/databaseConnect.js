import Mysql from "mysql2/promise"
import dotenv from "dotenv"

// configure the dotenv fikle
dotenv.config();

const connectToDatabase =  ()=>{
    try {
        const connection = new Mysql.createPool({
            host: process.env.DATABASE_HOST,
            user: process.env.DATABASE_USERNAME,
            password: process.env.DATABASE_PASSWORD,
            database: process.env.DATABASE_NAME,
            port:process.env.DATABASE_PORT,
        })
        console.log("Database connected successfully....");
        return connection;
    } catch (error) {
        console.error("Error Occured",error)
    }
}

const connection = await connectToDatabase();


export {connection}
