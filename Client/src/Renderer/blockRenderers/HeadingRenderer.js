import React from "react";
import SafeInlineRenderer from "../inline/SafeInlineRenderer";
import BlockWrapper from "../BlockWrapper";

export default function HeadingRenderer({ block, mode }) {
  if (!block.text) return null;

  const level = block.level || 2;
  const Tag = `h${level}`;

  return (
    <BlockWrapper block={block} mode={mode}>
      <Tag id={block.anchor || undefined}>
        <SafeInlineRenderer text={block.text} />
      </Tag>
    </BlockWrapper>
   
  );
}
