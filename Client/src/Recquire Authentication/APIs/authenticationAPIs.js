import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});


export const checkAuthentication =async ()=>{
    const res = await api.get(`/auth/test`);
    return res.data;
} 

export const login = async (email,password)=>{
    const res = await api.post(`/login`,{email,password});
    return res.data;
}

export const logout = async ()=>{
    const res = await api.get(`/logout`);
    return res.data;
}