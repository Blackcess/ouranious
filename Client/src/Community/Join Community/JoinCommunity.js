import { useRef, useState, useEffect } from "react";
import "./JoinCommunity.css";
import { AiOutlineSend } from "react-icons/ai";
import { createBenefiary } from "./APIs/communityAPIs";
import { toast } from "react-toastify";
import {verifyBeneficiary} from "../../Home/Apis/homepageApis"
import {useNavigate} from "react-router-dom"
import SpinLoader from "../../Util Components/SpinLoader/SpinLoader";

export function JoinCommunity() {
    const [accessCode, setAccessCode] = useState("");
    const [submitting, setSubmitting]  = useState(false)
    const [loading, setLoading] = useState(true)
    const navigation = useNavigate()

    useEffect(()=>{
        const verify = async ()=>{
            try{
                setLoading(true)
                const res = await verifyBeneficiary()
                if(res.status && res.data){
                    navigation(`/admin`)
                }
            }
            catch(error){
                console.error("Error verifying beneficiary (Client)", error)
                toast.error("Error verifying beneficiary")
            }
            finally{
                setLoading(false)
            }
        }

        verify()
    },[])

    const inputRef = useRef(null);

    const CODE_LENGTH = 6;

    const handleChange = (e) => {
        const value = e.target.value
            .replace(/\D/g, "")
            .slice(0, CODE_LENGTH);

        setAccessCode(value);
    };

    const handleBoxClick = () => {
        inputRef.current?.focus();
    };

    const handleSubmit = async ()=>{
        try {
            setSubmitting(true)
            const res = await createBenefiary(accessCode)
            if(res.status){
                toast.success("Registration Complete")
                navigation(`/admin`)
            }
            else{
                toast.error("Invalid Access Code")
            }
        } catch (error) {
            console.error("Error Creating Beneficiary (Client)", error)
        }
        finally{
            setSubmitting(false)
        }
    }

    if(loading){
        return (
            <div className="join-community-template">
                <SpinLoader/>
            </div>
        )
    }

    return (
        <section className="join-community-template">
            <h2 className="join-heading">
                Join
                <span className="ouranious-name"> Ouranious </span>
                Community
            </h2>

            <div
                className="access-code-wrap"
                onClick={handleBoxClick}
            >
                <input
                    ref={inputRef}
                    type="text"
                    value={accessCode}
                    onChange={handleChange}
                    maxLength={CODE_LENGTH}
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    className="hidden-access-input"
                />

                {[...Array(CODE_LENGTH)].map((_, index) => {
                    const digit = accessCode[index] || "";

                    const isActive =
                        index === accessCode.length &&
                        accessCode.length < CODE_LENGTH;

                    return (
                        <div
                            key={index}
                            className={`otp-box ${
                                isActive ? "active" : ""
                            }`}
                        >
                            {digit}
                        </div>
                    );
                })}
            </div>
            <p className="access-info">Enter Access Code from the Ouranious Development Team</p>
            { (accessCode.length === 6) &&
                <button 
                    className="sbt-access-code"
                    disabled = {(accessCode.length < 6)}
                    onClick={handleSubmit}
                >
                        <AiOutlineSend/>
                        Send
                </button>}
        </section>
    );
}