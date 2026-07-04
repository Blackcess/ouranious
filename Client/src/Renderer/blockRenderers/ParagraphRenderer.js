import React from "react";
import SafeInlineRenderer from "../inline/SafeInlineRenderer";
import BlockWrapper from "../BlockWrapper";

export default function ParagraphRenderer({ block, mode }) {
  if (!block.text || typeof block.text !== "string") {
    return null;
  }

  return (
    <BlockWrapper block={block} mode={mode}>
      <p>
        <SafeInlineRenderer text={block.text} />
      </p>
    </BlockWrapper>
    
  );
}
