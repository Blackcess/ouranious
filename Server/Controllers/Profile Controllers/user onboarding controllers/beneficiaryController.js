import { DomainError } from "../../../Domain Errors/domainErrors.js";
import { beneficiaryService, verifyBeneficiary } from "../../../Models/Profile Models/User Onboarding models/services/beneficiary.js";


export async function beneficiaryController(req, res, next){
    try {
        const userId = req.user.id
        const {accessCode} = req.body

        if(!accessCode){
            throw DomainError.invalid("Invalid AccessCode")
        }

        const result = await beneficiaryService(parseInt(accessCode), userId)
        if(result){
            res.status(200).json({
                status:true
            })
        }
        else{
            res.status(200).json({
                status:false
            })
        }
    } catch (error) {
        console.log("Error in registering beneficiary", error)
        res.status(500).json({
            msg:error
        })
    }

}


export async function verifyBeneficiaryController(req, res, next){
    try {
        const userId = req.user.id
        const result = await verifyBeneficiary(userId)
        res.status(200).json({
            status: true,
            data: result
        })
    }
    catch (error) {
        console.error("Error in verifying beneficiary", error)
        res.status(500).json({
            msg: error
        })
    }
}