import "./EditorComponent.css";
import React, { useEffect, useMemo, useRef } from "react";
// import Quill from "quill";
import MediaBlot from "./blots/media blots/MediaBlot";
import MediaPicker from "./Editor Helper Components/Media Picker Component/MediaPicker";
import { forwardRef } from "react";
import { useImperativeHandle } from "react";
import ReactQuill from "react-quill";
import Quill from "../quill";
import { IoImagesOutline } from "react-icons/io5";

Quill.register(MediaBlot, true);
// EditorComponent.js (no major change)
export const EditorComponent= forwardRef(({
  title,
  delta,
  onTitleChange,
  onDeltaChange,
  openMediaPicker,
  contentId
},ref)=> {


  const quillRef = useRef();
  useImperativeHandle(ref, ()=>({
    insertMedia(mediaId) {
      const quill = quillRef.current.getEditor();
      const range = quill.getSelection(true);
      console.log("Before",quill.scroll.descendants(Quill.import("blots/block/embed")));
      quill.insertEmbed(range.index, "media", mediaId, "user");
      quill.insertText(range.index + 1, "\n", "user");
      console.log("After",quill.getContents());
    },
  }))

  const modules = useMemo(() => ({
    toolbar: { 
      container: "#custom-toolbar",
      handlers: {
        insertMedia() {
          openMediaPicker();
          return false; // ⬅️ THIS LINE STOPS QUILL
        },
      }, 

    },
    history: { delay: 1000, maxStack: 100, userOnly: false },

  }), []);

  const formats = ["header", "bold", "italic", "underline", "blockquote","media"];
  useEffect(()=>{
    console.log("Delta is ",contentId)
  })
  
  return (
    <div className="editor-wrapper">
      <input
        type="text"
        value={title}
        onChange={(e) => onTitleChange(e.target.value)}
        placeholder="Title"
      />

      <div id="custom-toolbar">
        <select className="ql-header" defaultValue="">
          <option value="2">Heading 2</option>
          <option value="">Normal</option>
        </select>
        <button className="ql-bold" />
        <button className="ql-italic" />
        <button className="ql-underline" />
        <button className="ql-blockquote" />
        <button className="ql-insertMedia"><IoImagesOutline/></button>
      </div>

      {/* <button 
        onClick={openMediaPicker}
      > */}

     
      <ReactQuill
        key={contentId}
        ref={quillRef}
        defaultValue={delta}
        onChange={(content, delta, source, editor) => {
          onDeltaChange(editor.getContents());
        }}
        modules={modules}
        formats={formats}
        style={{ height: "100%", }}
      />
      
    </div>
  );
}
)

