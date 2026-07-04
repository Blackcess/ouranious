export default function MediaBlockRenderer({ block, mediaMap }) {
  const media = mediaMap[block.media_id];
  if (!media) {
    return (
      <div className="media-missing">
        <em>Media unavailable</em>
      </div>
    );
  }

  if (media.type === "image") {
    return (
      <figure className="media media-image">
        <img
          src={process.env.REACT_APP_API_BASE_URL + media.url}
          alt=""
          loading="lazy"
        />
      </figure>
    );
  }

  if (media.type === "video") {
    return (
      <figure className="media media-video">
        <iframe
          src={media.url}
          title="Embedded video"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </figure>
    );
  }

  return null;
}