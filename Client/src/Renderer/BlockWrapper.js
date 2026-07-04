import React from "react";

export default function BlockWrapper({ block, mode, children }) {
  const isAdmin = mode === "admin";
  const isPreview = mode === "preview";

  return (
    <>
        <div
            className={[
                "block",
                isAdmin ? "block--admin" : "",
                isPreview ? "block--preview" : ""
            ].join(" ")}
            data-block-type={block.type}
            data-block-id={isAdmin ? block.id : undefined}
        >
            {children}
        </div>
        {mode === "preview" && block.meta?.downgraded && (
            <div className="block-warning">
                ⚠️ This block was downgraded during conversion
            </div>
        )}
    </>
    
  );
}
