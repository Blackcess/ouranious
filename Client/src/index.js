import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter} from 'react-router-dom';
import App from './App';
import MyEditor from './Content Management/In Browser Text Editor/OuraniousTextEditor';
import QuillEditor from './Content Management/In Browser Text Editor/React Quill/QuillEditor';
import {ToastContainer} from "react-toastify"
import "react-toastify/dist/ReactToastify.css";




const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    
    <BrowserRouter>
        <ToastContainer/>
        <App/>
    </BrowserRouter>
    
);


