import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import ClaimLookup from "./ClaimLookup";
import ClaimDetails from "./ClaimDetails";
import ClaimSources from "./ClaimSources";
import ClaimStatusPanel from "./ClaimStatusPanel";
import AssessmentPanel from "./AssessmentPanel";
import AssessmentHistory from "./AssessmentHistory";
import MaterialisationPanel from "./MaterialisationPanel";

const claim = {
  id: "claim-1",
  status: "draft",
  created_at: "2026-10-24T10:00:00Z",
  research_notes: "Notes about the claim",
  source_ids: ["source-1"],
  proposition: { proposition_type: "identity_proposal", canonical_name: "Example entity" },
};

test("ClaimLookup presents loading state and forwards input and lookup events", () => {
  const onClaimIdChange = jest.fn();
  const onLookup = jest.fn();
  const { rerender } = render(<ClaimLookup claimIdInput="claim-1" onClaimIdChange={onClaimIdChange} onLookup={onLookup} loading disabled />);
  expect(screen.getByPlaceholderText("Claim UUID")).toHaveValue("claim-1");
  expect(screen.getByRole("button", { name: "Loading…" })).toBeDisabled();
  rerender(<ClaimLookup claimIdInput="claim-1" onClaimIdChange={onClaimIdChange} onLookup={onLookup} loading={false} disabled={false} />);
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: "claim-2" } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(onClaimIdChange).toHaveBeenCalled();
  expect(onLookup).toHaveBeenCalled();
});

test("ClaimDetails renders claim metadata and proposition", () => {
  render(<ClaimDetails claim={claim} />);
  expect(screen.getByRole("heading", { name: "Example entity" })).toBeInTheDocument();
  expect(screen.getByText("claim-1")).toBeInTheDocument();
  expect(screen.getByText("Notes about the claim")).toBeInTheDocument();
  expect(screen.getByText(/"canonical_name": "Example entity"/)).toBeInTheDocument();
});

test("ClaimSources shows loading, error, and empty states and forwards association actions", () => {
  const common = {
    claim: { ...claim, source_ids: [] }, sourceRecords: {}, associationId: " source-2 ",
    associationLoading: false, onAssociationIdChange: jest.fn(), onAttachSource: jest.fn(), onRemoveSource: jest.fn(),
  };
  const { rerender } = render(<ClaimSources {...common} sourcesLoading sourcesError={null} />);
  expect(screen.getByText("Loading source details…")).toBeInTheDocument();
  rerender(<ClaimSources {...common} sourcesLoading={false} sourcesError="Source lookup failed" />);
  expect(screen.getByRole("alert")).toHaveTextContent("Source lookup failed");
  expect(screen.getByText("No sources attached yet.")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Attach source" }));
  expect(common.onAttachSource).toHaveBeenCalledWith("source-2");
  fireEvent.change(screen.getByPlaceholderText("Source UUID"), { target: { value: "source-3" } });
  expect(common.onAssociationIdChange).toHaveBeenCalled();

  rerender(<ClaimSources {...common} claim={claim} sourceRecords={{ "source-1": { title: "Source title", source_type: "report" } }} sourcesLoading={false} sourcesError={null} />);
  expect(screen.getByText("Source title")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Remove" }));
  expect(common.onRemoveSource).toHaveBeenCalledWith("source-1");
});

test("ClaimStatusPanel forwards selected status and update action", () => {
  const onStatusTargetChange = jest.fn();
  const onUpdateStatus = jest.fn();
  const { rerender } = render(<ClaimStatusPanel statusTarget="" statusLoading={false} allowedTransitions={["accepted"]} onStatusTargetChange={onStatusTargetChange} onUpdateStatus={onUpdateStatus} />);
  fireEvent.change(screen.getByLabelText("Transition to"), { target: { value: "accepted" } });
  expect(onStatusTargetChange).toHaveBeenCalledWith("accepted");
  rerender(<ClaimStatusPanel statusTarget="accepted" statusLoading={false} allowedTransitions={["accepted"]} onStatusTargetChange={onStatusTargetChange} onUpdateStatus={onUpdateStatus} />);
  fireEvent.click(screen.getByRole("button", { name: "Update status" }));
  expect(onUpdateStatus).toHaveBeenCalled();
});

test("AssessmentPanel exposes required fields, options, and form submission", () => {
  const onAssessmentFormChange = jest.fn();
  const onSubmit = jest.fn((event) => event.preventDefault());
  render(<AssessmentPanel claim={claim} assessmentForm={{ outcome: "accept", rationale: "", assessed_by: "", review_process: "", transition_claim_to: "" }} assessmentSubmitting={false} onAssessmentFormChange={onAssessmentFormChange} onSubmit={onSubmit} />);
  expect(screen.getByLabelText("Rationale")).toBeRequired();
  expect(screen.getByLabelText("Assessed by")).toBeRequired();
  fireEvent.change(screen.getByLabelText("Rationale"), { target: { value: "Supported" } });
  fireEvent.change(screen.getByLabelText("Assessed by"), { target: { value: "Reviewer" } });
  expect(onAssessmentFormChange).toHaveBeenNthCalledWith(1, "rationale", "Supported");
  expect(onAssessmentFormChange).toHaveBeenNthCalledWith(2, "assessed_by", "Reviewer");
  fireEvent.submit(screen.getByLabelText("Rationale").closest("form"));
  expect(onSubmit).toHaveBeenCalled();
});

test("AssessmentHistory distinguishes loading, error and empty states and refreshes", () => {
  const onRefresh = jest.fn();
  const props = { assessments: [], onRefresh };
  const { rerender } = render(<AssessmentHistory {...props} assessmentsLoading assessmentsError={null} />);
  expect(screen.getByText("Loading assessment history…")).toBeInTheDocument();
  rerender(<AssessmentHistory {...props} assessmentsLoading={false} assessmentsError="History unavailable" />);
  expect(screen.getByRole("alert")).toHaveTextContent("History unavailable");
  rerender(<AssessmentHistory {...props} assessmentsLoading={false} assessmentsError={null} />);
  expect(screen.getByText("No assessments recorded.")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Refresh history" }));
  expect(onRefresh).toHaveBeenCalled();
});

test("MaterialisationPanel confirms actions, controls duplicate override, and renders blocked candidates", () => {
  const confirm = jest.spyOn(window, "confirm").mockReturnValue(true);
  const onAllowDuplicateChange = jest.fn();
  const onMaterialise = jest.fn();
  try {
    const blocked = {
      action: null, outcome: "possible_duplicate", target_kind: "identity", target_id: null,
      already_materialised: false, override_applied: false, candidates_truncated: true,
      candidates: [{ id: "candidate-1", canonical_name: "Possible match", kind: "organisation", match_kind: "possible" }],
    };
    render(<MaterialisationPanel allowDuplicate={false} materialisation={blocked} materialisationLoading={false} onAllowDuplicateChange={onAllowDuplicateChange} onMaterialise={onMaterialise} />);
    fireEvent.click(screen.getByLabelText("Allow possible duplicate"));
    expect(onAllowDuplicateChange).toHaveBeenCalledWith(true);
    fireEvent.click(screen.getByRole("button", { name: "Run materialisation" }));
    expect(confirm).toHaveBeenCalled();
    expect(onMaterialise).toHaveBeenCalled();
    expect(screen.getByText("Resolution blocked")).toBeInTheDocument();
    expect(screen.getByText("Possible match")).toBeInTheDocument();
    expect(screen.getByText(/Candidate list is truncated/)).toBeInTheDocument();
  } finally {
    confirm.mockRestore();
  }
});
