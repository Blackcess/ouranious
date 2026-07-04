import Quill from "../../../quill";

const BlockEmbed = Quill.import("blots/block/embed");

class MediaBlot extends BlockEmbed {
  static blotName = "media";
  static tagName = "div";
  static className = "ql-media";

  static create(mediaId) {
    const node = super.create();
    node.setAttribute("data-media-id", mediaId);
    // IMPORTANT:
    // No innerText, no text nodes, no contentEditable text
    node.setAttribute("contenteditable", "false");
     // 👇 Editor-only placeholder
    const placeholder = document.createElement("div");
    placeholder.className = "ql-media-placeholder";
    placeholder.innerText = "🖼 Ouranious Media";

    node.appendChild(placeholder);
    return node;
  }

  static value(node) {
    return node.getAttribute("data-media-id");
  }
  static formats() {
  return {};
}
}

export default MediaBlot;