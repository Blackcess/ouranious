import React from "react";
import ParagraphRenderer from "./blockRenderers/ParagraphRenderer";
import HeadingRenderer from "./blockRenderers/HeadingRenderer";
import BlockquoteRenderer from "./blockRenderers/BlockquoteRenderer";
import UnknownBlockRenderer from "./blockRenderers/UnknownBlockRenderer";
import MediaBlockRenderer from "./blockRenderers/MediaBlockRenderer";

const BLOCK_RENDERERS = {
  paragraph: ParagraphRenderer,
  heading: HeadingRenderer,
  blockquote: BlockquoteRenderer,
  media:MediaBlockRenderer
};

export default function ContentRenderer({ document, mode = "public",mediaMap = {} }) {
  if (!document || !Array.isArray(document.blocks)) {
    return null;
  }

  return (
    <>
      {document.blocks.map((block) => {
        const Renderer =
          BLOCK_RENDERERS[block.type] || UnknownBlockRenderer;

        return (
          <Renderer
            key={block.id}
            block={block}
            mode={mode}
            mediaMap={mediaMap}
          />
        );
      })}
    </>
  );
}
