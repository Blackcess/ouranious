import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const createTraditionalAccount = async (email, password, accountType, username) => {
    const res = await api.post(`/create_account/traditional`, {
        email,
        password,
        account_type: accountType,
        username
    })
    return res.data.status;
}
export const createAccountWithGoogle = async()=>{
    const res = await api.get("/auth/google");
    return res;
}

export const getOnboarding= async()=>{
    const res = await api.get("/onboarding/me");
    return res.data.data;
}

export const checkOnbordingViaEmail= async (email)=>{
    // console.log("Email in AOI is ",email)
    const res = await api.get(`/onboarding/email/${email}`)
    return res.data.data
}
export const saveIdentity= async (persona)=>{
    const res = await api.patch("/onboarding/identity",{
        persona
    })
    return res.data.message;
}
export const saveIntrests= async (intrests)=>{
    console.log("Interests are ", intrests)
    const res = await api.put("/onboarding/interests",{
        interests:intrests
    })
    return res.data.message;
}
export const savePreferences= async (acquisition_source, preferred_content_region)=>{
    const res = await api.patch("/onboarding/preferences",{
        acquisition_source,
        preferred_content_region
    })
    return res.data.message;
}
export const completeOnboarding = async()=>{
    const res = await api.post("/onboarding/complete");
    return res.data.message;
}