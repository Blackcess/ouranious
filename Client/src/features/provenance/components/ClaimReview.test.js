import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import ClaimReview from "./ClaimReview";
import { provenanceApi } from "../../../api/provenance/provenanceApi";

jest.mock("../../../api/provenance/provenanceApi", () => ({
  enums: {
    assessmentOutcomes: ["accept", "reject"],
    allowedStatusTransitions: { draft: ["accepted"], accepted: [] },
  },
  provenanceApi: {
    getClaim: jest.fn(),
    getSource: jest.fn(),
    getAssessments: jest.fn(),
    addSource: jest.fn(),
    removeSource: jest.fn(),
    updateClaimStatus: jest.fn(),
    createAssessment: jest.fn(),
    materialise: jest.fn(),
  },
}));

const claimOne = {
  id: "claim-one",
  status: "draft",
  research_notes: "First claim notes",
  created_at: "2026-10-24T10:00:00Z",
  source_ids: [],
  proposition: { proposition_type: "identity_proposal", identity_kind: "organisation", canonical_name: "First claim", aliases: [], attributes: {} },
};
const claimTwo = {
  ...claimOne,
  id: "claim-two",
  research_notes: "Second claim notes",
  proposition: { ...claimOne.proposition, canonical_name: "Second claim" },
};
const source = {
  id: "source-one",
  title: "Primary source",
  source_type: "report",
  publisher: "Publisher",
  publication_date: "2026-10-20",
};
const assessment = {
  id: "assessment-one",
  outcome: "accept",
  assessed_by: "Reviewer",
  rationale: "Evidence supports this claim.",
  assessed_at: "2026-10-24T10:01:00Z",
  review_process: null,
};

beforeEach(() => {
  jest.clearAllMocks();
  provenanceApi.getAssessments.mockResolvedValue([]);
  provenanceApi.getSource.mockResolvedValue(source);
});

test("supports an empty review state and loads the initial claim with sources and history", async () => {
  const { unmount } = render(<ClaimReview />);
  expect(screen.getByRole("heading", { name: "Start with a claim ID" })).toBeInTheDocument();
  unmount();

  const claimWithSource = { ...claimOne, source_ids: [source.id] };
  provenanceApi.getClaim.mockResolvedValue(claimWithSource);
  provenanceApi.getAssessments.mockResolvedValue([assessment]);
  render(<ClaimReview initialClaimId={claimOne.id} />);

  expect(await screen.findByRole("heading", { name: "First claim" })).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Claim UUID")).toHaveValue(claimOne.id);
  expect(await screen.findByText("Primary source")).toBeInTheDocument();
  expect(screen.getByText("Evidence supports this claim.")).toBeInTheDocument();
  expect(provenanceApi.getClaim).toHaveBeenCalledWith(claimOne.id);
  expect(provenanceApi.getSource).toHaveBeenCalledWith(source.id);
  expect(provenanceApi.getAssessments).toHaveBeenCalledWith(claimOne.id);
});

test("shows failed claim and source-detail loads distinctly", async () => {
  provenanceApi.getClaim.mockRejectedValueOnce(new Error("Claim was not found."));
  const { rerender } = render(<ClaimReview initialClaimId="missing-claim" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("Claim was not found.");
  expect(screen.getByRole("heading", { name: "Start with a claim ID" })).toBeInTheDocument();

  provenanceApi.getClaim.mockResolvedValueOnce({ ...claimOne, source_ids: [source.id] });
  provenanceApi.getSource.mockRejectedValueOnce(new Error("Source was not found."));
  rerender(<ClaimReview initialClaimId="claim-with-missing-source" />);
  expect(await screen.findByRole("heading", { name: "First claim" })).toBeInTheDocument();
  expect(await screen.findByText("Source was not found.")).toBeInTheDocument();
  expect(screen.getByText("Source details unavailable")).toBeInTheDocument();
});

test("lookup selects a different claim and an earlier slow response cannot replace it", async () => {
  let finishFirstLoad;
  provenanceApi.getClaim
    .mockImplementationOnce(() => new Promise((resolve) => { finishFirstLoad = resolve; }))
    .mockResolvedValueOnce(claimTwo);
  render(<ClaimReview initialClaimId={claimOne.id} />);

  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: claimTwo.id } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("heading", { name: "Second claim" })).toBeInTheDocument();
  finishFirstLoad(claimOne);
  await waitFor(() => expect(provenanceApi.getClaim).toHaveBeenCalledTimes(2));
  expect(screen.queryByRole("heading", { name: "First claim" })).not.toBeInTheDocument();
  expect(screen.getByPlaceholderText("Claim UUID")).toHaveValue(claimTwo.id);
});

test("attaches and removes sources through the API and reloads the selected claim", async () => {
  provenanceApi.getClaim
    .mockResolvedValueOnce(claimOne)
    .mockResolvedValueOnce({ ...claimOne, source_ids: [source.id] })
    .mockResolvedValue(claimOne);
  provenanceApi.addSource.mockResolvedValue({ status: 204, data: null });
  provenanceApi.removeSource.mockResolvedValue({ status: 204, data: null });
  render(<ClaimReview initialClaimId={claimOne.id} />);
  await screen.findByRole("heading", { name: "First claim" });

  fireEvent.change(screen.getByPlaceholderText("Source UUID"), { target: { value: source.id } });
  fireEvent.click(screen.getByRole("button", { name: "Attach source" }));
  await waitFor(() => expect(provenanceApi.addSource).toHaveBeenCalledWith(claimOne.id, source.id));
  await waitFor(() => expect(provenanceApi.getClaim).toHaveBeenCalledTimes(2));

  fireEvent.click(await screen.findByRole("button", { name: "Remove" }));
  await waitFor(() => expect(provenanceApi.removeSource).toHaveBeenCalledWith(claimOne.id, source.id));
  await waitFor(() => expect(provenanceApi.getClaim).toHaveBeenCalledTimes(3));
});

test("updates claim status and submits assessments with nullable fields then refreshes history", async () => {
  provenanceApi.getClaim.mockResolvedValue(claimOne);
  provenanceApi.updateClaimStatus.mockResolvedValue({ ...claimOne, status: "accepted" });
  provenanceApi.createAssessment.mockResolvedValue({ assessment, claim_status: null });
  provenanceApi.getAssessments
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([assessment]);
  render(<ClaimReview initialClaimId={claimOne.id} />);
  await screen.findByRole("heading", { name: "First claim" });

  fireEvent.change(screen.getByLabelText("Transition to"), { target: { value: "accepted" } });
  fireEvent.click(screen.getByRole("button", { name: "Update status" }));
  expect(await screen.findByText("Claim status updated.")).toBeInTheDocument();
  expect(provenanceApi.updateClaimStatus).toHaveBeenCalledWith(claimOne.id, "accepted");

  fireEvent.change(screen.getByLabelText("Rationale"), { target: { value: assessment.rationale } });
  fireEvent.change(screen.getByLabelText("Assessed by"), { target: { value: assessment.assessed_by } });
  fireEvent.click(screen.getByRole("button", { name: "Record assessment" }));
  expect(await screen.findByText("Assessment recorded.")).toBeInTheDocument();
  expect(provenanceApi.createAssessment).toHaveBeenCalledWith(claimOne.id, {
    outcome: "accept",
    rationale: assessment.rationale,
    assessed_by: assessment.assessed_by,
    review_process: null,
    transition_claim_to: null,
  });
  expect(screen.getByText(assessment.rationale)).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Refresh history" }));
  expect(await screen.findByText(assessment.rationale)).toBeInTheDocument();
  expect(provenanceApi.getAssessments).toHaveBeenCalledTimes(2);
});

test("keeps status-update errors local to the review workflow", async () => {
  provenanceApi.getClaim.mockResolvedValue(claimOne);
  provenanceApi.updateClaimStatus.mockRejectedValueOnce(new Error("Transition is not allowed."));
  render(<ClaimReview initialClaimId={claimOne.id} />);
  await screen.findByRole("heading", { name: "First claim" });

  fireEvent.change(screen.getByLabelText("Transition to"), { target: { value: "accepted" } });
  fireEvent.click(screen.getByRole("button", { name: "Update status" }));
  expect(await screen.findByRole("status")).toHaveTextContent("Transition is not allowed.");
  expect(screen.getByRole("heading", { name: "First claim" })).toBeInTheDocument();
});

test("shows assessment-history load failures separately from an empty history", async () => {
  provenanceApi.getClaim.mockResolvedValue(claimOne);
  provenanceApi.getAssessments.mockRejectedValueOnce(new Error("History unavailable."));
  render(<ClaimReview initialClaimId={claimOne.id} />);

  await screen.findByRole("heading", { name: "First claim" });
  expect(await screen.findByRole("alert")).toHaveTextContent("History unavailable.");
  expect(screen.queryByText("No assessments recorded.")).not.toBeInTheDocument();

  provenanceApi.getAssessments.mockResolvedValueOnce([]);
  fireEvent.click(screen.getByRole("button", { name: "Refresh history" }));
  expect(await screen.findByText("No assessments recorded.")).toBeInTheDocument();
});

test("preserves blocked materialisation responses and clears the result when selecting another claim", async () => {
  provenanceApi.getClaim.mockResolvedValueOnce(claimOne).mockResolvedValueOnce(claimTwo);
  provenanceApi.materialise.mockResolvedValue({
    status: 409,
    data: {
      claim_id: claimOne.id,
      target_kind: "identity",
      target_id: null,
      outcome: "possible_duplicate",
      action: null,
      override_applied: false,
      already_materialised: false,
      candidates: [{ id: "candidate-one", kind: "organisation", canonical_name: "Possible match", match_kind: "possible", evidence: {} }],
      candidates_truncated: true,
    },
  });
  const confirm = jest.spyOn(window, "confirm").mockReturnValue(true);
  try {
    render(<ClaimReview initialClaimId={claimOne.id} />);
    await screen.findByRole("heading", { name: "First claim" });
    fireEvent.click(screen.getByRole("button", { name: "Run materialisation" }));
    expect(await screen.findByText("Resolution blocked")).toBeInTheDocument();
    expect(screen.getByText("Possible match")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: claimTwo.id } });
    fireEvent.click(screen.getByRole("button", { name: "Load" }));
    expect(await screen.findByRole("heading", { name: "Second claim" })).toBeInTheDocument();
    expect(screen.queryByText("Resolution blocked")).not.toBeInTheDocument();
    expect(screen.queryByText("Possible match")).not.toBeInTheDocument();
  } finally {
    confirm.mockRestore();
  }
});
