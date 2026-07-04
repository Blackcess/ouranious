import { DomainError } from "../../../Domain Errors/domainErrors.js";
import { Router } from "express";
import { authenticationMiddleware } from "../../../Middlewares/authenticationMiddleware.js";
import { beneficiaryController, verifyBeneficiaryController} from "../../../Controllers/Profile Controllers/user onboarding controllers/beneficiaryController.js";

export const beneficiaryRouter = Router()

beneficiaryRouter.post("/",authenticationMiddleware,beneficiaryController)
beneficiaryRouter.get("/verify",authenticationMiddleware,verifyBeneficiaryController)




