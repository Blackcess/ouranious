import { provenanceApi } from "./provenanceApi";
import { ApiError } from "./errors";
import { decodeTypedValue, parseJsonValue } from "./typedValueCodec";

const response = (status, body) => ({ status, ok: status >= 200 && status < 300, text: async () => body === undefined ? "" : JSON.stringify(body) });
const claimId = "5e45ed40-cced-4ad2-8cd1-320f41fe0747";

beforeEach(() => { global.fetch = jest.fn(); });

test("uses versioned source and claim endpoint paths and serializes payloads", async () => {
  global.fetch.mockResolvedValueOnce(response(201, { id: "source-id" }));
  await provenanceApi.createSource({ title: "Paper", source_type: "report" });
  expect(global.fetch.mock.calls[0][0]).toMatch(/\/api\/v1\/sources$/);
  expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({ title: "Paper", source_type: "report" });

  global.fetch.mockResolvedValueOnce(response(201, { id: claimId, proposition: { proposition_type: "identity_proposal", attributes: { "$type": "dict", items: [["team", "research"]] } } }));
  const claim = await provenanceApi.createClaim({ proposition: { proposition_type: "identity_proposal", identity_kind: "organisation", canonical_name: "Example", aliases: [], attributes: {} } });
  expect(global.fetch.mock.calls[1][0]).toMatch(/\/api\/v1\/claims$/);
  expect(claim.proposition.attributes).toEqual({ team: "research" });
});

test("handles an empty 204 source association without JSON parsing", async () => {
  global.fetch.mockResolvedValueOnce(response(204));
  const result = await provenanceApi.addSource(claimId, "source-id");
  expect(global.fetch.mock.calls[0][1].method).toBe("POST");
  expect(result.status).toBe(204);
  expect(result.data).toBeNull();
});

test("uses the declared status, detach, and assessment routes", async () => {
  global.fetch.mockResolvedValueOnce(response(200, { id: claimId, status: "accepted" }));
  await provenanceApi.updateClaimStatus(claimId, "accepted");
  expect(global.fetch.mock.calls[0][0]).toMatch(new RegExp(`/claims/${claimId}/status$`));
  expect(global.fetch.mock.calls[0][1].method).toBe("PATCH");
  expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({ status: "accepted" });

  global.fetch.mockResolvedValueOnce(response(204));
  await provenanceApi.removeSource(claimId, "source-id");
  expect(global.fetch.mock.calls[1][0]).toMatch(new RegExp(`/claims/${claimId}/sources/source-id$`));
  expect(global.fetch.mock.calls[1][1].method).toBe("DELETE");

  global.fetch.mockResolvedValueOnce(response(200, []));
  await provenanceApi.getAssessments(claimId);
  expect(global.fetch.mock.calls[2][0]).toMatch(new RegExp(`/claims/${claimId}/assessments$`));
  global.fetch.mockResolvedValueOnce(response(200, { id: "assessment-id" }));
  await provenanceApi.getAssessment("assessment-id");
  expect(global.fetch.mock.calls[3][0]).toMatch(/\/assessments\/assessment-id$/);
});

test("returns materialisation conflict body as a domain result", async () => {
  const blocked = { claim_id: claimId, target_kind: "identity", target_id: null, outcome: "possible_duplicate", action: null, override_applied: false, already_materialised: false, candidates: [{ id: "candidate-id", kind: "organisation", canonical_name: "Example", match_kind: "exact", evidence: {} }], candidates_truncated: true };
  global.fetch.mockResolvedValueOnce(response(409, blocked));
  const result = await provenanceApi.materialise(claimId, false);
  expect(result.status).toBe(409);
  expect(result.data).toEqual(blocked);
});

test("preserves structured HTTP details and reports transport errors", async () => {
  global.fetch.mockResolvedValueOnce(response(422, { detail: "Invalid proposition" }));
  await expect(provenanceApi.getClaim(claimId)).rejects.toMatchObject({ status: 422, detail: "Invalid proposition" });
  global.fetch.mockRejectedValueOnce(new Error("offline"));
  await expect(provenanceApi.getClaim(claimId)).rejects.toBeInstanceOf(ApiError);
});

test("accepts ordinary JSON and decodes only registered typed tags", () => {
  expect(parseJsonValue('{"ordinary":[1,true]}')).toEqual({ ordinary: [1, true] });
  expect(() => parseJsonValue('{"$type":"mystery"}')).toThrow(/unsupported typed-value tag/i);
  expect(decodeTypedValue({ "$type": "date", value: "2026-10-24" })).toBe("2026-10-24");
  expect(decodeTypedValue({ "$type": "dict", items: [["a", 1]] })).toEqual({ a: 1 });
});
