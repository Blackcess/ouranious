import { createMedia } from "../repository/media.repository.js";
import { DomainError } from "../../../Domain Errors/domainErrors.js";

function validateVideoUrl(url) {
  if (url.includes("youtube.com") || url.includes("youtu.be")) {
    return { provider: "youtube", embedUrl: url };
  }

  if (url.includes("vimeo.com")) {
    return { provider: "vimeo", embedUrl: url };
  }

  return null;
}

export async function addExternalVideo({
  url,
  authorId,
}) {
  const validated = validateVideoUrl(url);

  if (!validated) {
    throw DomainError.invalid("UNSUPPORTED_VIDEO_PROVIDER");
  }

  const mediaId = await createMedia({
    type: "video",
    source: "external",
    url: validated.embedUrl,
    createdBy: authorId,
  });

  return {
    mediaId,
    url: validated.embedUrl,
  };
}