import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import ClaimCreator from "./ClaimCreator";
import { provenanceApi } from "../../../api/provenance/provenanceApi";

jest.mock("../../../api/provenance/provenanceApi", () => ({
  enums: {
    identityKinds: ["organisation", "person"],
    relationshipTypes: ["founded", "born_in"],
  },
  provenanceApi: { createClaim: jest.fn() },
}));

const createdClaim = {
  id: "new-claim-id",
  status: "draft",
  proposition: { proposition_type: "identity_proposal", canonical_name: "Example" },
};
const sourceOne = "5e45ed40-cced-4ad2-8cd1-320f41fe0747";
const sourceTwo = "9e45ed40-cced-4ad2-8cd1-320f41fe0747";

beforeEach(() => jest.clearAllMocks());

test("renders proposition controls and preserves only research notes when switching types", () => {
  render(<ClaimCreator onClaimCreated={jest.fn()} />);

  expect(screen.getByRole("heading", { name: "Propose a knowledge change" })).toBeInTheDocument();
  expect(screen.getByLabelText(/Canonical name/)).toBeRequired();
  expect(screen.getByLabelText(/Identity kind/)).toHaveValue("organisation");

  fireEvent.change(screen.getByLabelText(/Canonical name/), { target: { value: "Temporary name" } });
  fireEvent.change(screen.getByPlaceholderText("Context, caveats, and what should be verified"), { target: { value: "Keep these notes" } });
  fireEvent.change(screen.getByPlaceholderText("UUID, UUID"), { target: { value: sourceOne } });
  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "identity_attribute" } });

  expect(screen.getByLabelText(/Identity UUID/)).toBeRequired();
  expect(screen.queryByLabelText(/Canonical name/)).not.toBeInTheDocument();
  expect(screen.getByPlaceholderText("Context, caveats, and what should be verified")).toHaveValue("Keep these notes");
  expect(screen.getByPlaceholderText("UUID, UUID")).toHaveValue("");

  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "relationship" } });
  expect(screen.getByLabelText(/Source identity UUID/)).toBeRequired();
  expect(screen.getByLabelText(/Target identity UUID/)).toBeRequired();
  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "relationship_property" } });
  expect(screen.getByLabelText(/Relationship UUID/)).toBeRequired();
  expect(screen.getByLabelText(/Property name/)).toBeRequired();

  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "identity_proposal" } });
  expect(screen.getByLabelText(/Canonical name/)).toHaveValue("");
});

test("submits identity proposal payload with parsed sources, notes, aliases, and JSON attributes", async () => {
  const onClaimCreated = jest.fn();
  provenanceApi.createClaim.mockResolvedValue(createdClaim);
  render(<ClaimCreator onClaimCreated={onClaimCreated} />);

  fireEvent.change(screen.getByLabelText(/Canonical name/), { target: { value: "Example" } });
  fireEvent.change(screen.getByLabelText(/Aliases/), { target: { value: "Example Inc.\n Example Corporation \n" } });
  fireEvent.change(screen.getByLabelText(/Attributes/), { target: { value: '{"founded": 2020}' } });
  fireEvent.change(screen.getByPlaceholderText("UUID, UUID"), { target: { value: " invalid-source,\nstill-invalid " } });
  fireEvent.change(screen.getByPlaceholderText("Context, caveats, and what should be verified"), { target: { value: "Research context" } });

  expect(screen.getByText(/"source_ids": \[/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));

  expect(await screen.findByText("Claim created.")).toBeInTheDocument();
  expect(provenanceApi.createClaim).toHaveBeenCalledWith({
    proposition: {
      proposition_type: "identity_proposal",
      identity_kind: "organisation",
      canonical_name: "Example",
      aliases: ["Example Inc.", "Example Corporation"],
      attributes: { founded: 2020 },
    },
    source_ids: ["invalid-source", "still-invalid"],
    research_notes: "Research context",
  });
  expect(onClaimCreated).toHaveBeenCalledTimes(1);
  expect(onClaimCreated).toHaveBeenCalledWith(createdClaim);
  expect(screen.getByLabelText(/Canonical name/)).toHaveValue("Example");
});

test("preserves identity attribute and relationship proposition request shapes", async () => {
  provenanceApi.createClaim.mockResolvedValue(createdClaim);
  render(<ClaimCreator onClaimCreated={jest.fn()} />);

  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "identity_attribute" } });
  fireEvent.change(screen.getByLabelText(/Identity UUID/), { target: { value: sourceOne } });
  fireEvent.change(screen.getByLabelText(/Attribute name/), { target: { value: "website" } });
  fireEvent.change(screen.getByLabelText(/Proposed value/), { target: { value: '{"$type":"date","value":"2026-10-24"}' } });
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));
  await waitFor(() => expect(provenanceApi.createClaim).toHaveBeenNthCalledWith(1, {
    proposition: {
      proposition_type: "identity_attribute",
      identity_id: sourceOne,
      attribute_name: "website",
      proposed_value: { $type: "date", value: "2026-10-24" },
    },
    source_ids: [],
    research_notes: "",
  }));

  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "relationship" } });
  fireEvent.change(screen.getByLabelText(/Source identity UUID/), { target: { value: sourceOne } });
  fireEvent.change(screen.getByLabelText(/Target identity UUID/), { target: { value: sourceTwo } });
  fireEvent.change(screen.getByLabelText(/Relationship type/), { target: { value: "founded" } });
  fireEvent.change(screen.getByLabelText(/Existing relationship UUID/), { target: { value: sourceTwo } });
  fireEvent.change(screen.getByLabelText(/Relationship properties/), { target: { value: '{"founding_role":"CEO"}' } });
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));

  await waitFor(() => expect(provenanceApi.createClaim).toHaveBeenNthCalledWith(2, {
    proposition: {
      proposition_type: "relationship",
      source_identity_id: sourceOne,
      target_identity_id: sourceTwo,
      relationship_type: "founded",
      existing_relationship_id: sourceTwo,
      properties: { founding_role: "CEO" },
    },
    source_ids: [],
    research_notes: "",
  }));

  fireEvent.change(screen.getByLabelText(/Proposition type/), { target: { value: "relationship_property" } });
  fireEvent.change(screen.getByLabelText(/Relationship UUID/), { target: { value: sourceOne } });
  fireEvent.change(screen.getByLabelText(/Property name/), { target: { value: "founding_date" } });
  fireEvent.change(screen.getByLabelText(/Proposed value/), { target: { value: '"2020-01-01"' } });
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));
  await waitFor(() => expect(provenanceApi.createClaim).toHaveBeenNthCalledWith(3, {
    proposition: {
      proposition_type: "relationship_property",
      relationship_id: sourceOne,
      property_name: "founding_date",
      proposed_value: "2020-01-01",
    },
    source_ids: [],
    research_notes: "",
  }));
});

test("keeps invalid and incomplete propositions disabled and reports API errors locally", async () => {
  const onClaimCreated = jest.fn();
  render(<ClaimCreator onClaimCreated={onClaimCreated} />);

  expect(screen.getByRole("button", { name: "Create claim" })).toBeDisabled();
  fireEvent.change(screen.getByLabelText(/Canonical name/), { target: { value: "Example" } });
  fireEvent.change(screen.getByLabelText(/Attributes/), { target: { value: "{" } });
  expect(screen.getByText("Enter valid JSON in the value fields.")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Create claim" })).toBeDisabled();
  expect(provenanceApi.createClaim).not.toHaveBeenCalled();

  fireEvent.change(screen.getByLabelText(/Attributes/), { target: { value: "{}" } });
  provenanceApi.createClaim.mockRejectedValueOnce(new Error("Claim rejected by API."));
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));
  expect(await screen.findByText("Claim rejected by API.")).toBeInTheDocument();
  expect(onClaimCreated).not.toHaveBeenCalled();
});

test("shows the submitting state and invokes the callback once after success", async () => {
  let finishCreate;
  const onClaimCreated = jest.fn();
  provenanceApi.createClaim.mockImplementation(() => new Promise((resolve) => { finishCreate = resolve; }));
  render(<ClaimCreator onClaimCreated={onClaimCreated} />);

  fireEvent.change(screen.getByLabelText(/Canonical name/), { target: { value: "Example" } });
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));
  expect(screen.getByRole("button", { name: "Submitting…" })).toBeDisabled();
  finishCreate(createdClaim);

  expect(await screen.findByText("Claim created.")).toBeInTheDocument();
  expect(onClaimCreated).toHaveBeenCalledTimes(1);
  expect(onClaimCreated).toHaveBeenCalledWith(createdClaim);
});
