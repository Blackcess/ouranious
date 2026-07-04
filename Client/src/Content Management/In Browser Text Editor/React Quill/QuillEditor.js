import "./QuillEditor.css";
import { useState,useEffect,useRef } from "react";
import ReactQuill,{Quill} from "react-quill";
import ImageResize from "quill-image-resize-module-react"
import {ImageDrop} from "quill-image-drop-module";
import "react-quill/dist/quill.snow.css";
import axios from "axios";

const API_BASE_URL  =  process.env.REACT_APP_API_BASE_URL;
function QuillEditor(){
    Quill.register('modules/imageResize', ImageResize);
    Quill.register('modules/imageDrop', ImageDrop);
    const [editorContent,setEditorContent] = useState("");
    const [deltaContent,setDeltaContent] = useState(null);
    const quillRef = useRef(null);


    const handleChange = (content,delta,source,editor)=>{
        setEditorContent(content);
        setDeltaContent(quillRef.current.getEditor().getContents());
        const dataToSave = {
            content: quillRef.current.getEditor().getContents(),
            undo: quillRef.current.getEditor().history.stack.undo,
            redo: quillRef.current.getEditor().history.stack.redo
        }
        localStorage.setItem("quill-editor-data",JSON.stringify(dataToSave));

    }
    const modules = {
        toolbar:[
            [{ 'header': [1, 2,3,4, false] }],
            [{font:[]}],
            ['image']
            [{align:[ ]}],
            ['bold', 'italic', 'underline','strike', 'blockquote', 'code-block', 'link', 'image', 'video'],
            [{ 'list': 'ordered'}, { 'list': 'bullet' },
            // [{ 'script': 'sub'}, { 'script': 'super' }],
            // [{ 'indent': '-1'}, { 'indent': '+1' }],
            // [{ 'direction': 'rtl' }],
            // [{ 'size': ['small', false, 'large', 'huge'] }],
            // [{ 'color': [] }, { 'background': [] }],
            // [{ 'font': [] }],
            // [{ 'align': [] }]
            ],
            ['link', 'video'],
            ['clean']
        ],
        history:{
            delay:2000,
            maxStack:500,
            userOnly:true

        },
        imageResize:{
            parchment: Quill.import('parchment'),
            modules: [ 'Resize', 'DisplaySize', 'Toolbar' ]
        },
        imageDrop:true

    }
    const fomats =[
        "header","bold","italic","underline","strike","blockquote","code-block","link","image","video","list","bullet","script","indent","direction","size","color","background","font","align"
    ]

    useEffect(()=>{
        //    ue the localstorage to persist editor datya plus history stack data
        const saved = localStorage.getItem("quill-editor-data");
        if(saved){
            const {content,undo,redo} = JSON.parse(saved);
            const editor = quillRef.current.getEditor();
            editor.setContents(content);
            // restore history stack
            editor.history.stack.undo = undo || [];
            editor.history.stack.redo = redo || [];
        }
    },[])


    return(<>
        <div className="my-quill-editor-template">
            {/* <h2>My Very First Quill Editor...</h2> */}
            <ReactQuill
            ref={quillRef}
            theme="snow" 
            value={editorContent}
            onChange={handleChange}
            modules={modules}
            formats={fomats}
            />
            <button onClick={()=>{
                (quillRef.current)&& quillRef.current.getEditor().history.undo();
            }}>Undo</button>
            <button onClick={()=>{
                (quillRef.current) && quillRef.current.getEditor().history.redo()
            }}>Redo</button>
            

            <hr/>
            {/* <div className="editor-content-display"
              dangerouslySetInnerHTML={{__html:editorContent}}>
            </div> */}
            <h4>Output...</h4>
            <div className="react-quill-output-render">
                <pre>
                    {JSON.stringify(deltaContent,null,2)}
                </pre>
               
            </div>
        </div>
    </>)
    
}

export default QuillEditor;