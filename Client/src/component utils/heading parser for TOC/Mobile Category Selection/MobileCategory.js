import "./MobileCategory.css"
import { useEffect, useState } from "react"
import React from 'react';
import axios from "axios";
import { NavLink } from "react-router-dom";

const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
// const categories = [
//   'Technology', 'Health', 'Finance', 'Travel', 'Education', 
//   'Sports', 'Lifestyle', 'Entertainment', 'Science', 'Food',
//   // You can dynamically fetch categories from your backend
// ];

const MobileCategoryPage = () => {
    const [allCategories,setAllCategories] = useState([])
    const [categoriesLoaded,setCategoriesLoaded] = useState(false)
    useEffect(()=>{
        getCategories()
    },[])
    const getCategories= async()=>{
            try {
                const res= await axios.get(`${API_BASE_URL}/category`,{
                    withCredentials:true
                })
                if(res.data.status){
                    // console.log("Mobile Categories are: ",res.data);
                    setAllCategories(res.data.data)
                    setCategoriesLoaded(true)
                }
    
            } catch (error) {
                console.error(error )
                setCategoriesLoaded(false)
            }
        }
  return (
    <div className="category-page">
      <h1 className="category-title">All Categories</h1>
      <div className="category-grid">
        {allCategories.map((category, index) => (
          <div key={index} className="category-card">
            <NavLink to={`/ourans-platform/category?categoryId=${category.category_id}&categoryName=${category.name}`} className="category-link">
              {category.name}
            </NavLink>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MobileCategoryPage;