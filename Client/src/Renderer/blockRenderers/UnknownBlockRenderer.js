import React from "react";

export default function UnknownBlockRenderer({ block, mode }) {
  if (mode === "admin" || mode === "preview") {
    return (
      <div style={{ border: "1px dashed red", padding: "8px" }}>
        Unknown block type: <strong>{block.type}</strong>
      </div>
    );
  }

  return null;
}
