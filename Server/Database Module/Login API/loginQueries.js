import { connection } from "../Database Connection/databaseConnect.js";

const checkByUserName = async (username)=>{
    
    try {
       const [row]=await connection.query(`SELECT * FROM users WHERE name = ?`,[username]);
       if(!row.length){
        throw new Error("User Not Found")
       } 
       return row;
    } catch (error) {
        console.error("error: ",error)
        throw new Error("User not Found")
    }
}

const createTraditionalAccount= async (username,password,account_type)=>{
    try {
        if(!(username && password)){
            throw new Error("Invalid Credentials")
        }
        const [search_result] = await connection.query(`SELECT * FROM users WHERE name = ?`,[username]);
        if(search_result.length){
            throw new Error ("user with this username already exists")
        }
        const [{affectedRows,insertId}]=await connection.query(`INSERT INTO users (create_time,name,password,account_type)
                                VALUES(NOW(),?,?,?)`,[username,password,account_type]);
        if(!affectedRows){
            throw new Error("Error Inserting new user")
        }
        console.log("User Inserted Successsfully");
        return true
    } catch (error) {
        console.error(error);
        throw new Error(error);
    }
}

// await createTraditionalAccount("Thomas","thomas123")

export {checkByUserName,createTraditionalAccount}