export function uuid() {
  if (crypto?.randomUUID) {
    return crypto.randomUUID();
  }

  // fallback
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
}

function normalizeOps(ops) {
  const normalized = [];

  for (const op of ops) {
    // Only split string inserts
    if (typeof op.insert === "string" && op.insert.includes("\n")) {
      const parts = op.insert.split("\n");

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];

        // Text before newline
        if (part.length > 0) {
          normalized.push({
            insert: part,
            attributes: op.attributes,
          });
        }

        // Newline (except after last split)
        if (i < parts.length - 1) {
          normalized.push({
            insert: "\n",
            attributes: op.attributes,
          });
        }
      }
    } else {
      // Already atomic
      normalized.push(op);
    }
  }

  return normalized;
}


function serializeInline(text, attributes = {}) {
  let output = text;

  if (attributes.link) {
    output = `<a href="${attributes.link}">${output}</a>`;
  }

  if (attributes.bold) {
    output = `<strong>${output}</strong>`;
  }

  if (attributes.italic) {
    output = `<em>${output}</em>`;
  }

  if (attributes.underline) {
    output = `<u>${output}</u>`;
  }

  return output;
}


function createParagraphBlock(text, meta) {
  const block = {
    id: uuid(),
    type: "paragraph",
    text,
  };

  if (meta) {
    block.meta = meta;
  }

  return block;
}

function createHeadingBlock(text) {
  return {
    id: uuid(),
    type: "heading",
    level: 2,
    text,
    anchor: slugify(text),
  };
}

function createBlockquoteBlock(text) {
  return {
    id: uuid(),
    type: "blockquote",
    text,
  };
}

function createMediaBlock(media_id) {
  return {
    id: uuid(),
    type: "media",
    media_id: String(media_id),
  };
}

function createBlockFromNewline(text, attributes = {}) {
  // Heading 2
  if (attributes.header === 2) {
    return createHeadingBlock(text);
  }

  // Blockquote
  if (attributes.blockquote === true) {
    return createBlockquoteBlock(text);
  }

  // Unsupported block formats → downgrade
  const unsupportedKeys = Object.keys(attributes).filter(
    key => key !== "header" && key !== "blockquote"
  );

  if (unsupportedKeys.length > 0) {
    return createParagraphBlock(text, {
      downgradedFrom: unsupportedKeys.join(","),
    });
  }

  // Default paragraph
  return createParagraphBlock(text);
}

// export function deltaToContentDocument(delta) {
//   const blocks = [];
//   let currentText = "";

//   const normalizedOps = normalizeOps(delta.ops);

//   for (const op of normalizedOps) {
//     // Text insert
//     if (typeof op.insert === "string" && op.insert !== "\n") {
//       const serialized = serializeInline(op.insert, op.attributes);
//       currentText += serialized;
//       continue;
//     }

//     // Newline = block boundary
//     if (op.insert === "\n") {
//       // Ignore empty lines
//       if (currentText.trim() === "") {
//         currentText = "";
//         continue;
//       }

//       const block = createBlockFromNewline(
//         currentText,
//         op.attributes
//       );

//       blocks.push(block);
//       currentText = "";
//     }
//   }

//   return {
//     version: 1,
//     blocks,
//   };
// }


export function deltaToContentDocument(delta) {
  const blocks = [];
  let currentText = "";

  const normalizedOps = normalizeOps(delta.ops);

  for (const op of normalizedOps) {

    // ✅ MEDIA EMBED (NEW)
    if (
      typeof op.insert === "object" &&
      op.insert !== null &&
      op.insert.media
    ) {
      // Flush pending text before media
      if (currentText.trim() !== "") {
        blocks.push(
          createParagraphBlock(currentText)
        );
        currentText = "";
      }

      blocks.push(
        createMediaBlock(op.insert.media)
      );

      continue;
    }

    // Text insert
    if (typeof op.insert === "string" && op.insert !== "\n") {
      const serialized = serializeInline(op.insert, op.attributes);
      currentText += serialized;
      continue;
    }

    // Newline = block boundary
    if (op.insert === "\n") {
      if (currentText.trim() === "") {
        currentText = "";
        continue;
      }

      const block = createBlockFromNewline(
        currentText,
        op.attributes
      );

      blocks.push(block);
      currentText = "";
    }
  }

  return {
    version: 1,
    blocks,
  };
}
