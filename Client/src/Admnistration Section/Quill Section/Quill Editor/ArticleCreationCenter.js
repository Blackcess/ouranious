import "./ArticleCreationCenter.css";
import React, { useState, useEffect } from "react";
import { loadDraft, saveDraft,publishContent,getAllCategories } from "./APIs/quillEditorAPIs";
import { createNewEditorState } from "./editor utilitis/editorState.factory";
import { deltaToContentDocument } from "../../../Content Management/Articles/Content Documents Style/tools/deltaToContentDocument";
import { useMemo } from "react";
import ArticleView from "../../../Content Management/Articles/Content Documents Style/ArticleViewer";
import ArticleBody from "../../../Content Management/Articles/Content Documents Style/ArticleBody";
import { useNavigate } from "react-router-dom";
import MediaPicker from "./Editor Helper Components/Media Picker Component/MediaPicker";
import { useRef } from "react";
import {EditorComponent} from "./EditorComponent"
import ArticleThumbnail from "../../../Content Management/Articles/Content Documents Style/Thumbnails/Article Thumbnail/ArticleThumbnail";
import { CategorySelect } from "./Editor Helper Components/Category Selector/CategorySelector";


export default function ArticleEditorPage() {

  const [editorState, setEditorState] = useState(createNewEditorState());
  const [isLoading, setIsLoading] = useState(true);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [showMediaPicker, setShowMediaPicker] = useState(false);
  const [mediaPickerMode, setMediaPickerMode] = useState(null);
  const [categories, setCategories] = useState([]);
  const navigate= useNavigate()
  const editorRef = useRef(null);
  // Get contentId from query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const contentId = urlParams.get("contentId");


 useEffect(() => {
    async function hydrate() {
      console.log("ContentId = ", contentId);
      try {
        const categoryResponse = await getAllCategories()
        setCategories(categoryResponse)
      } catch (error) {
        console.error(error)
      }

      if (!contentId) {
        setIsLoading(false);
        return;
      }

      try {
        const draft = await loadDraft(contentId);

        setEditorState((prev) => ({
          ...prev,
          contentId: draft.contentId,
          title: draft.title,
          delta: draft.delta,
          type: draft.type,
          mode: "edit",
          isDirty: false,
          lastSavedAt: draft.lastSavedAt,
          thumbnailMediaId:draft.thumbnailMediaId,
          categoryId: draft.categoryId ?? null, 
        }));
      } catch (err) {
        // No draft exists → start new draft session
        setEditorState((prev) => ({
          ...prev,
          contentId,
          mode: "edit",
        }));
      } finally {
        setIsLoading(false);
      }
    }

    hydrate();
  }, [contentId]);

  useEffect(() => {
  function beforeUnload(e) {
    if (!editorState.isDirty) return;
    e.preventDefault();
    e.returnValue = "";
  }

  window.addEventListener("beforeunload", beforeUnload);
  return () => window.removeEventListener("beforeunload", beforeUnload);
}, [editorState.isDirty]);

const previewBlocks = useMemo(() => {
  if (!isPreviewing || !editorState.delta) return null;
  // console.log("Preview Blocks:", deltaToContentDocument(editorState.delta));   
  return deltaToContentDocument(editorState.delta);
}, [isPreviewing, editorState.delta]);


function handleTitleChange(newTitle) {
    setEditorState((prev) => ({
      ...prev,
      title: newTitle,
      isDirty: true,
    }));
  }

function handleDeltaChange(newDelta) {
    setEditorState((prev) => ({
      ...prev,
      delta: newDelta,
      isDirty: true,
    }));
}

async function handleSaveDraft() {
  setEditorState((prev) => ({
    ...prev,
    isSaving: true,
    error: null,
  }));

  try {
    const result = await saveDraft({
      contentId: editorState.contentId,
      title: editorState.title,
      delta: editorState.delta,
      type: editorState.type,
      thumbnailMediaId: editorState.thumbnailMediaId,
      categoryId:editorState.categoryId,   
    });

    setEditorState((prev) => ({
      ...prev,
      contentId: result.contentId,
      isDirty: false,
      isSaving: false,
      lastSavedAt: result.lastSavedAt,
    }));
  } catch (err) {
    setEditorState((prev) => ({
      ...prev,
      isSaving: false,
      error: "Failed to save draft",
    }));
  }
}

function openPreview() {
  if (!editorState.delta) return;
  setIsPreviewing(true);
}

function closePreview() {
  setIsPreviewing(false);
}

async function handlePublish() {
  if (editorState.isDirty) return;

  setEditorState((prev) => ({
    ...prev,
    isSaving: true,
    error: null,
  }));

  try {
    await publishContent(editorState.contentId);

    // Editor lifecycle ends here
    navigate(`/home`);
  } catch (err) {
    setEditorState((prev) => ({
      ...prev,
      isSaving: false,
      error: "Failed to publish content",
    }));
  }
}

function openMediaPicker() {
  setMediaPickerMode("body");
  setShowMediaPicker(true);
}
function openThumbnailPicker() {
  setMediaPickerMode("thumbnail");
  setShowMediaPicker(true);
}

function handleMediaSelect(mediaId) {
  if (mediaPickerMode === "body") {
    editorRef.current?.insertMedia(mediaId);
  }

  if (mediaPickerMode === "thumbnail") {
    setEditorState(prev => ({
      ...prev,
      thumbnailMediaId: mediaId,
      isDirty: true,
    }));
  }

  setShowMediaPicker(false);
  setMediaPickerMode(null);
}

  const editorSessionKey = useMemo(
    () => contentId ?? "new-draft",
    [contentId]
  );



  if (isLoading) {
    return <div className="loading-editor-template">Loading editor…</div>;
  }

  return (
    <div className="article-editor-page">
      {(!isPreviewing)&&<header className="editor-toolbar">
        {/* desktop */}
        {/* DESKTOP TOOLBAR */}
        <div className="editor-toolbar-desktop">
          <div className="editor-toolbar-left">
            <button
              onClick={handleSaveDraft}
              disabled={
                editorState.isSaving ||
                !editorState.isDirty ||
                !editorState.delta ||
                !editorState.title
              }
            >
              {editorState.isSaving ? "Saving…" : "Save Draft"}
            </button>

            <button
              onClick={openPreview}
              disabled={!editorState.delta}
            >
              Preview
            </button>

            <div className="thumbnail-toolbar">
              <div className="thumbnail-hover-zone">
                <button
                  className="thumbnail-action"
                  onClick={openThumbnailPicker}
                >
                  🖼 {editorState.thumbnailMediaId
                    ? "Change thumbnail"
                    : "Add thumbnail"}
                </button>

                {editorState.thumbnailMediaId && (
                  <span className="thumbnail-status">selected</span>
                )}

                {editorState.thumbnailMediaId && (
                  <div className="thumbnail-preview">
                    <ArticleThumbnail mediaId={editorState.thumbnailMediaId} />
                  </div>
                )}
                <CategorySelect
                  categories={categories}
                  value={editorState.categoryId}
                  onChange={(categoryId) =>
                    setEditorState(prev => ({
                      ...prev,
                      categoryId,
                      isDirty: true,
                    }))
                  }
                />
                {!editorState.categoryId && (
                  <small className="hint-category">
                    Choose a category before publishing
                  </small>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* MOBILE TOOLBAR */}
        <div className="editor-toolbar-mobile">
          <div className="editor-toolbar-left">
            <button onClick={handleSaveDraft}>💾</button>

            <div className="editor-more">
              <button className="more-button">⋯</button>

              <div className="more-menu">
                <button onClick={openPreview}>Preview</button>

                <button onClick={openThumbnailPicker}>
                  {editorState.thumbnailMediaId
                    ? "Change thumbnail"
                    : "Add thumbnail"}
                </button>

                {/* CATEGORY SELECT (MOBILE) */}
                <div className="mobile-category">
                  {/* <label>Category</label> */}
                  <CategorySelect
                    categories={categories}
                    value={editorState.categoryId}
                    onChange={(categoryId) =>
                      setEditorState(prev => ({
                        ...prev,
                        categoryId,
                        isDirty: true,
                      }))
                    }
                  />
                  {!editorState.categoryId && (
                        <small className="hint-category">
                          Choose a category before publishing
                        </small>
                      )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT SIDE (shared) */}
        <div className="editor-toolbar-right">
          <button
            className="primary"
            onClick={handlePublish}
            disabled={
              editorState.isDirty ||
              editorState.isSaving ||
              !editorState.contentId ||
              !editorState.categoryId
            }
          >
            Publish
          </button>
        </div>
      </header>}

      <main className="editor-main">
      {isPreviewing && previewBlocks ? (
        <section className="editor-preview">
          <button onClick={closePreview} className="back-button">
            ← Back to editor
          </button>

          <ArticleBody document={previewBlocks} redirect={{status:true, from:"article-creation-center"}}/>
        </section>
      ) : (
        <section className="editor-content-temp">
          <EditorComponent
            ref={editorRef}
            title={editorState.title}
            delta={editorState.delta}
            onTitleChange={handleTitleChange}
          onDeltaChange={handleDeltaChange}
          openMediaPicker={openMediaPicker}
          contentId={editorSessionKey}
        />  
        </section>
      )}
    </main>
     {showMediaPicker && (
      <div className="modal-overlay">
        <div className="modal-content">
          <MediaPicker
            onSelect={handleMediaSelect}
            onClose={() => setShowMediaPicker(false)}
          />
        </div>
      </div>
    )}
      
      
    </div>
  );

}
