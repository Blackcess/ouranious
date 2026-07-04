export function createNewEditorState() {
  return {
    // Identity
    contentId: null,
    slug: null,

    // Core content
    title: "",
    delta: null,

    // Metadata
    type: "article",
    status: "draft",
    thumbnailMediaId:null,
    categoryId:null,   

    // Lifecycle
    mode: "create",
    isDirty: false,
    isSaving: false,
    lastSavedAt: null,

    // Error handling
    error: null,
  };
}
