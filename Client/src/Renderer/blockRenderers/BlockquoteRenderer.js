import React from "react";
import SafeInlineRenderer from "../inline/SafeInlineRenderer";
import BlockWrapper from "../BlockWrapper";

export default function BlockquoteRenderer({ block,mode }) {
  if (!block.text) return null;

  return (
    <BlockWrapper block={block} mode={mode}>
      <blockquote>
        <SafeInlineRenderer text={block.text} />
      </blockquote>
    </BlockWrapper>
    
  );
}
