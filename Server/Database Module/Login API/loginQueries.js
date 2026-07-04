import { connection } from "../Database Connection/databaseConnect.js";
import { DomainError } from "../../Domain Errors/domainErrors.js";
import bycrpt from "bcrypt";

const checkByUserName = async (username)=>{
    
    try {
       const [row]=await connection.query(`SELECT * FROM users WHERE username = ?`,[username]);
       if(!row.length){
        throw DomainError.notFound("User Not Found")
       } 
       return row;
    } catch (error) {
        console.error("error: ",error)
        throw error;
    }
}
const checkByEmail = async (email)=>{
    const [row]=await connection.query(`SELECT * FROM users WHERE email = ?`,[email]);
    if(!row.length){
     throw DomainError.notFound("User Not Found")
    }
    return row;
}

const createTraditionalAccount= async (email,password,username,account_type)=>{
    try {
        if(!(email && password && username)){
            throw DomainError.invalid("Invalid Credentials")
        }
        const [search_result] = await connection.query(`SELECT * FROM users WHERE email = ?`,[email]);
        if(search_result.length){
            throw DomainError.invalid("user with this email already exists")
        }
        const hashedPassword = await bycrpt.hash(password,10);
        
        const [{affectedRows,insertId}]=await connection.query(`INSERT INTO users (create_time,email,password,account_type,username)
                                VALUES(NOW(),?,?,?,?)`,[email,hashedPassword,account_type,username]);
        if(!affectedRows){
            throw DomainError.invalid("Error Inserting new user")
        }
        console.log("User Inserted Successsfully");
        return true
    } catch (error) {
        console.error(error);
        throw error;
    }
}

// await createTraditionalAccount("Thomas","thomas123")

export {checkByUserName,createTraditionalAccount}