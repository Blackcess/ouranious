import { request } from "./httpClient";
import { decodeClaimValues } from "./typedValueCodec";

const id = (value) => encodeURIComponent(value.trim());
const data = (promise) => promise.then((result) => result.data);
export const provenanceApi = {
  createSource: (body) => data(request("/sources", { method: "POST", body })),
  getSource: (sourceId) => data(request(`/sources/${id(sourceId)}`)),
  createClaim: (body) => data(request("/claims", { method: "POST", body })).then(decodeClaimValues),
  getClaim: (claimId) => data(request(`/claims/${id(claimId)}`)).then(decodeClaimValues),
  updateClaimStatus: (claimId, status) => data(request(`/claims/${id(claimId)}/status`, { method: "PATCH", body: { status } })).then(decodeClaimValues),
  addSource: (claimId, sourceId) => request(`/claims/${id(claimId)}/sources/${id(sourceId)}`, { method: "POST" }),
  removeSource: (claimId, sourceId) => request(`/claims/${id(claimId)}/sources/${id(sourceId)}`, { method: "DELETE" }),
  createAssessment: (claimId, body) => data(request(`/claims/${id(claimId)}/assessments`, { method: "POST", body })),
  getAssessments: (claimId) => data(request(`/claims/${id(claimId)}/assessments`)),
  getAssessment: (assessmentId) => data(request(`/assessments/${id(assessmentId)}`)),
  materialise: (claimId, allow_possible_duplicate = false) => request(`/claims/${id(claimId)}/materialisation`, { method: "POST", body: { allow_possible_duplicate }, acceptStatuses: [409] }),
};

export const enums = {
  sourceTypes: ["official_website", "news_article", "report", "government_record", "academic_publication", "database", "social_media", "other"],
  claimStatuses: ["draft", "pending_review", "accepted", "rejected", "disputed", "needs_research", "superseded"],
  allowedStatusTransitions: {
    draft: ["pending_review", "needs_research", "superseded"],
    pending_review: ["accepted", "rejected", "disputed", "needs_research", "superseded"],
    accepted: ["disputed", "superseded"],
    rejected: ["pending_review", "superseded"],
    disputed: ["pending_review", "accepted", "rejected", "superseded"],
    needs_research: ["pending_review", "superseded"],
    superseded: [],
  },
  assessmentOutcomes: ["accept", "reject", "request_more_research", "flag_dispute"],
  identityKinds: ["person", "organisation", "place", "industry", "product", "technology"],
  relationshipTypes: ["founded", "leads", "owns", "born_in", "lives_in", "partnered_with", "invested_in", "acquired", "headquartered_in", "operates_in", "operates_in_industry", "offers", "develops", "uses", "built_with", "available_in", "located_in", "part_of"],
};
