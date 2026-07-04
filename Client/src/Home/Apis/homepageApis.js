import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

//recommendations
export const getRecommemendedHomeAricles = async ()=>{
    const res = await api.get(`/content/recommendations?context=home`);
    return res.data.data
}

// verify beneficiary
export const verifyBeneficiary = async ()=>{
    const res = await api.get(`/beneficiary/verify`);
    return res.data;
}

// verify authentication
export const verifyAuthentication = async ()=>{
    const res = await api.get(`/auth/test`);
    return res.data
}
