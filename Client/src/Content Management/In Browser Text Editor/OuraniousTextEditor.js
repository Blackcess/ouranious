import React, { useEffect } from "react";
import { EditorContent, useEditor } from "@tiptap/react"
import starterKit from "@tiptap/starter-kit"
import Image from "@tiptap/extension-image"
import Bold from "@tiptap/extension-bold"
import Italic from "@tiptap/extension-italic"
import Underline from "@tiptap/extension-underline"
import Heading from "@tiptap/extension-heading"
import "./OuraniousTextEditor.css"
import { Form } from "react-router-dom";
import axios from "axios";

const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;

export default function MyEditor(){
  const editor = useEditor({
    extensions:[starterKit,
                Image,
                Bold,
                Italic,
                Underline,
                Heading.configure({levels:[1,2,3]})],
    content: "<p>Hello Creator! Start writing your article ...</p>"
  })
  useEffect(()=>{
    console.log("Button Statuses is: ",editor.isActive("bold"))
  },[editor.isActive("bold")])

  return <>
    <div className="editor-container">
      {/* upload image input */}
      <form>
        <input 
          type="file"
          accept="image/*"
          style={{display:"none"}}
          id="editor-imageUpload"
          onChange={async (e)=>{
            const file = e.target.files[0];
            if(file){
              const formData= new FormData()
              formData.append("myArticle",file)
              // send to backend
              const res = await axios.post(`${API_BASE_URL}/createArticle/upload`,{
                withCredentials:true
              })
              console.log("Backend Receivers : ",res)
            }
          }}
        />
      </form>
        
      <div className="toolbar">
        <button onClick={()=> editor.chain().focus().toggleBold().run()}
          className={editor.isActive("bold") ? "is-active": ""}>Bold</button>
        <button onClick={()=> editor.chain().focus().toggleItalic().run()}
          className={editor.isActive("italic") ? "is-active": ""}>Italic</button>
        <button onClick={()=> editor.chain().focus().toggleUnderline().run()}
          className={editor.isActive("underline") ? "is-active": ""}>Underline</button>
        <button onClick={()=>editor.chain().focus().toggleHeading({level:1}).run()}
          className={editor.isActive("heading",{level:1}) ? "is-active": ""}>H1</button>
        <button onClick={()=>editor.chain().focus().toggleHeading({level:2}).run() }
          className={editor.isActive("heading",{level:2}) ? "is-active": ""}>H2</button>
        
      </div>  
      <EditorContent editor={editor}/>
    </div>
  
  </>
}