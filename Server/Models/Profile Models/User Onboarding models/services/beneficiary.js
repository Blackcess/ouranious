import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";
import { DomainError } from "../../../../Domain Errors/domainErrors.js";

const BENEFICIARY_ACCESS_CODE = 145264;

export async function beneficiaryService(accessCode, userId){
    console.log(userId)
    if(accessCode !== BENEFICIARY_ACCESS_CODE){
        return false
    }

    const result = await connection.execute(`
            UPDATE users 
            SET is_beneficiary = 1
            WHERE id = ?
        `,
    [userId])
    
    return true

}

export async function verifyBeneficiary(userId){
    const [rows] = await connection.execute(`
        SELECT is_beneficiary
        FROM users
        WHERE id = ?
    `, [userId]);


    if (rows.length === 0) {
        throw DomainError.invalid("User not found");
    }

    const isBeneficiary = rows[0].is_beneficiary === 1;
    return isBeneficiary;
    
}