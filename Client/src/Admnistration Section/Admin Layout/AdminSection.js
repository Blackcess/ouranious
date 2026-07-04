import { useEffect, useState } from "react";
import "./AdminSection.css";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../Recquire Authentication/useAuth";
import { AdminNavigation } from "./Admin Navigation/AdminNavigation";
import { MyArticles } from "./My Articles/MyArticles";
import { verifyAuthentication, verifyBeneficiary } from "../../Home/Apis/homepageApis";
import { toast } from "react-toastify";

const AdminLayout = () => {
  const sessionData = useAuth();
  const navigate = useNavigate()

  useEffect(()=>{
    const checkAuth = async () => {
      try {
        const isAuthenticated = await verifyAuthentication();
        const isBeneficiary = await verifyBeneficiary();
        console.log("BeneficiaryStatus:", isBeneficiary);

        if ( !isAuthenticated.status) {
          navigate("/login");
        }

        if (!isBeneficiary.data) {
          toast.error("You are not a beneficiary. Please contact the Ouranious Team.");
          navigate("/community");
        }

  
      } catch (error) {
        console.error("Error verifying authentication", error);
        navigate("/login");
      }
    };

    checkAuth();
  }, []);

  return (
    <div className="admin-container">
      <AdminNavigation/>
      <MyArticles/>
      <Outlet/>
    </div>
  );
};

export default AdminLayout;
