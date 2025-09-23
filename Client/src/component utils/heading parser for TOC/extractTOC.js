import { useEffect, useState } from "react";

function useExtractHeadings(htmlString) {
  const [headings, setHeadings] = useState([]);

  useEffect(() => {
    if (!htmlString) return;

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, "text/html");

    const nodes = doc.querySelectorAll("h2[id], h3[id]");
    const extracted = Array.from(nodes).map(node => ({
      id: node.id,
      text: node.textContent,
      level: node.tagName.toLowerCase(),
    }));

    setHeadings(extracted);
  }, [htmlString]);

  return headings;
}
export default useExtractHeadings;
