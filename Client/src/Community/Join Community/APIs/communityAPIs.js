import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export async function createBenefiary(accessCode){
    const res = await api.post("/beneficiary",{
        accessCode: accessCode
    })
    return res.data
}