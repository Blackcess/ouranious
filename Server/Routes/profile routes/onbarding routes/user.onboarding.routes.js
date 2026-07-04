import  {Router} from 'express'
import { 
    getMyOnboardingController,
    updateIdentityController,
    updateInterestsController,
    updatePreferencesController,
    completeOnboardingController,
    checkOnboardingStatusViaEmailController
 } from '../../../Controllers/Profile Controllers/user onboarding controllers/user.onboarding.profile.controllers.js'
import { 
    validateIdentity,
    validateInterests,
    validatePreferences
 } from '../../../Models/Profile Models/User Onboarding models/user.onboarding.validation.js'
import { authenticationMiddleware } from '../../../Middlewares/authenticationMiddleware.js'

const onboardingRouter = Router();

onboardingRouter.get("/me", authenticationMiddleware, getMyOnboardingController);

onboardingRouter.get("/email/:email", authenticationMiddleware, checkOnboardingStatusViaEmailController);

onboardingRouter.patch("/identity", authenticationMiddleware, validateIdentity, updateIdentityController);

onboardingRouter.put("/interests", authenticationMiddleware, validateInterests, updateInterestsController);

onboardingRouter.patch("/preferences", authenticationMiddleware, validatePreferences, updatePreferencesController);

onboardingRouter.post("/complete", authenticationMiddleware, completeOnboardingController);

export default onboardingRouter;