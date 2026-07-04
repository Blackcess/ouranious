// ArticleThumbnail.jsx
import "./ArticleThumbnail.css";
import { useEffect, useState } from "react";
import { getMediaById } from "../../APIs/contentDocumentAPI";

export default function ArticleThumbnail({ mediaId }) {
  const [media, setMedia] = useState(null);
//   const [loading,setLoading] = useState()

  useEffect(() => {
    if (!mediaId) return;

    async function load() {
      const result = await getMediaById(mediaId);
      setMedia(result);
    }

    load();
  }, [mediaId]);

  if (!media) return null;

  return (
    <div className="article-thumbnail">
      <img
        src={process.env.REACT_APP_API_BASE_URL + media.url}
        alt={media.alt || ""}
        loading="eager"
      />
    </div>
  );
}
