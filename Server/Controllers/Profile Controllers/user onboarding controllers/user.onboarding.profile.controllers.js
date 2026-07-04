import { DomainError } from "../../../Domain Errors/domainErrors.js";
import { 
    ensureOnboardingProfile,
    getOnboardingProfile,
    updateIdentity,
    updateInterests,
    updatePreferences,
    completeOnboarding,
    checkOnboardingStatusFromEmail
 } from "../../../Models/Profile Models/User Onboarding models/services/user.onboarding.services.js";

 export const getMyOnboardingController = async (req, res, next) => {
    try {
        const userId = req.user.id;

        // guarantee profile exists
        await ensureOnboardingProfile(userId);

        const profile = await getOnboardingProfile(userId);

        return res.status(200).json({
            data: profile
        });

    } catch (err) {
        next(err);
    }
};

export const checkOnboardingStatusViaEmailController= async (req,res)=>{
    const {email} = req.params
    console.log("Email is ",req.params)
    if(email.trim()==="")  throw DomainError.invalid("Invalid  Email Address")
    const result= await checkOnboardingStatusFromEmail(email)
    res.status(200).json({
        data:result
    })  
}

export const updateIdentityController = async (req, res, next) => {
    try {   
        const userId = req.user.id;
        const { persona } = req.body;

        await updateIdentity(userId, persona);

        return res.status(200).json({
            message: "Identity updated successfully"
        });

    } catch (err) {
        next(err);
    }
};

export const updateInterestsController = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const { interests } = req.body;
        

        await updateInterests(userId, interests);

        return res.status(200).json({
            message: "Interests updated successfully"
        });

    } catch (err) {
        next(err);
    }
};


export const updatePreferencesController = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const { acquisition_source, preferred_content_region } = req.body;
        if(acquisition_source.trim() ==="" && preferred_content_region.trim() === "") {
            return res.status(200).json({
                message: "No Content Reorded"
            });
        }

        await updatePreferences(userId, {
            acquisition_source,
            preferred_content_region
        });

        return res.status(200).json({
            message: "Preferences updated successfully"
        });

    } catch (err) {
        next(err);
    }
};

export const completeOnboardingController = async (req, res, next) => {
    try {
        const userId = req.user.id;

        await completeOnboarding(userId);

        return res.status(200).json({
            message: "Onboarding completed successfully"
        });

    } catch (err) {
        next(err);
    }
};