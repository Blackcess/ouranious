import React from "react";
import { tokenizeInlineText } from "./inlineTokenizer";

const ALLOWED_TAGS = {
  strong: "strong",
  em: "em",
  u: "u",
  a: "a",
};

function isSafeUrl(url) {
  try {
    const parsed = new URL(url, window.location.origin);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export default function SafeInlineRenderer({ text }) {
  const tokens = tokenizeInlineText(text);
  const stack = [];
  const output = [];

  const pushNode = (node) => {
    if (stack.length > 0) {
      stack[stack.length - 1].children.push(node);
    } else {
      output.push(node);
    }
  };

  tokens.forEach((token, index) => {
    // Match opening or closing tag with optional attributes
    const openTagMatch = token.match(/^<([a-z]+)([^>]*)>$/);
    const closeTagMatch = token.match(/^<\/([a-z]+)>$/);

    // Plain text
    if (!openTagMatch && !closeTagMatch) {
      pushNode(token);
      return;
    }

    // Closing tag
    if (closeTagMatch) {
      const tagName = closeTagMatch[1];
      if (!ALLOWED_TAGS[tagName]) {
        pushNode(token);
        return;
      }

      const last = stack.pop();
      if (!last) return;

      const element =
        last.tag === "a"
          ? React.createElement(
              "a",
              {
                key: index,
                href: last.href,
                target: "_blank",
                rel: "noopener noreferrer",
              },
              last.children
            )
          : React.createElement(
              last.tag,
              { key: index },
              last.children
            );

      pushNode(element);
      return;
    }

    // Opening tag
    if (openTagMatch) {
      const tagName = openTagMatch[1];
      const attrString = openTagMatch[2];

      if (!ALLOWED_TAGS[tagName]) {
        pushNode(token);
        return;
      }

      // Special handling for <a>
      if (tagName === "a") {
        const hrefMatch = attrString.match(/href\s*=\s*"([^"]+)"/);

        if (!hrefMatch || !isSafeUrl(hrefMatch[1])) {
          // Unsafe or missing href → render as text
          pushNode(token);
          return;
        }

        stack.push({
          tag: "a",
          href: hrefMatch[1],
          children: [],
        });
        return;
      }

      // Normal inline tag
      stack.push({
        tag: ALLOWED_TAGS[tagName],
        children: [],
      });
    }
  });

  return <>{output}</>;
}
