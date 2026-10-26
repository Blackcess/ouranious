import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import ProvenanceWorkspace from "./ProvenanceWorkspace";
import { provenanceApi } from "../../api/provenance/provenanceApi";

jest.mock("../../api/provenance/provenanceApi", () => ({
  enums: { sourceTypes: ["report"], claimStatuses: ["draft", "accepted"], allowedStatusTransitions: { draft: ["accepted"] }, assessmentOutcomes: ["accept"], identityKinds: ["organisation"], relationshipTypes: ["founded"] },
  provenanceApi: { getClaim: jest.fn(), getAssessments: jest.fn(), createAssessment: jest.fn(), materialise: jest.fn(), createClaim: jest.fn(), createSource: jest.fn(), getSource: jest.fn(), addSource: jest.fn(), removeSource: jest.fn(), updateClaimStatus: jest.fn() },
}));

const claim = { id: "5e45ed40-cced-4ad2-8cd1-320f41fe0747", status: "draft", research_notes: "Research", created_at: "2026-10-24T10:00:00Z", source_ids: [], proposition: { proposition_type: "identity_proposal", identity_kind: "organisation", canonical_name: "Example", aliases: [], attributes: {} } };

beforeEach(() => jest.clearAllMocks());

test("claim form switches controls for all four proposition variants", () => {
  render(<ProvenanceWorkspace />);
  fireEvent.click(within(screen.getByRole("navigation", { name: "Provenance workflows" })).getByRole("button", { name: "Create claim" }));
  expect(screen.getByLabelText(/Canonical name/)).toBeInTheDocument();
  const selector = screen.getByLabelText(/Proposition type/);
  fireEvent.change(selector, { target: { value: "identity_attribute" } });
  expect(screen.getByLabelText(/Identity UUID/)).toBeInTheDocument();
  fireEvent.change(selector, { target: { value: "relationship" } });
  expect(screen.getByLabelText(/Source identity UUID/)).toBeInTheDocument();
  fireEvent.change(selector, { target: { value: "relationship_property" } });
  expect(screen.getByLabelText(/Relationship UUID/)).toBeInTheDocument();
});

test("claim review preserves and displays multiple assessment records", async () => {
  provenanceApi.getClaim.mockResolvedValue(claim);
  provenanceApi.getAssessments.mockResolvedValue([
    { id: "assessment-1", outcome: "accept", assessed_by: "A. Reviewer", rationale: "Evidence supports the claim.", assessed_at: "2026-10-24T10:01:00Z", review_process: null },
    { id: "assessment-2", outcome: "request_more_research", assessed_by: "B. Reviewer", rationale: "Check the filing date.", assessed_at: "2026-10-24T10:02:00Z", review_process: "Peer review" },
  ]);
  render(<ProvenanceWorkspace />);
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: claim.id } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("heading", { name: /Assessment history/ })).toBeInTheDocument();
  expect(screen.getByText("Evidence supports the claim.")).toBeInTheDocument();
  expect(screen.getByText("Check the filing date.")).toBeInTheDocument();
});

test("nullable assessment status and blocked materialisation are shown faithfully", async () => {
  provenanceApi.getClaim.mockResolvedValue(claim);
  provenanceApi.getAssessments.mockResolvedValue([]);
  const assessment = { id: "assessment-new", outcome: "accept", assessed_by: "Researcher", rationale: "Reviewed sources.", assessed_at: "2026-10-24T10:01:00Z", review_process: null };
  provenanceApi.createAssessment.mockResolvedValue({ assessment, claim_status: null });
  provenanceApi.materialise.mockResolvedValue({ status: 409, data: { claim_id: claim.id, target_kind: "identity", target_id: null, outcome: "possible_duplicate", action: null, override_applied: false, already_materialised: false, candidates: [{ id: "candidate-1", kind: "organisation", canonical_name: "Example Org", match_kind: "possible", evidence: {} }], candidates_truncated: true } });
  const confirm = jest.spyOn(window, "confirm").mockReturnValue(true);
  render(<ProvenanceWorkspace />);
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: claim.id } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  await screen.findByRole("heading", { name: "Example" });
  fireEvent.change(screen.getByLabelText(/Rationale/), { target: { value: "Reviewed sources." } });
  fireEvent.change(screen.getByLabelText(/Assessed by/), { target: { value: "Researcher" } });
  fireEvent.click(screen.getByRole("button", { name: "Record assessment" }));
  expect(await screen.findByText("Reviewed sources.")).toBeInTheDocument();
  expect(provenanceApi.createAssessment).toHaveBeenCalledWith(claim.id, expect.objectContaining({ transition_claim_to: null }));
  await waitFor(() => expect(screen.getByRole("button", { name: "Run materialisation" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "Run materialisation" }));
  expect(await screen.findByText("Resolution blocked")).toBeInTheDocument();
  expect(screen.getByText(/Candidate list is truncated/)).toBeInTheDocument();
  expect(screen.getByText("Example Org")).toBeInTheDocument();
  confirm.mockRestore();
});
