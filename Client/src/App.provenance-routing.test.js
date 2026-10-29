import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, useLocation, useNavigate } from "react-router-dom";
import App from "./App";
import { checkAuthentication } from "./Recquire Authentication/APIs/authenticationAPIs";
import { provenanceApi } from "./api/provenance/provenanceApi";

jest.mock("./Parent Page/ParentComponent", () => {
  const React = require("react");
  const { Outlet } = require("react-router-dom");
  return {
    __esModule: true,
    default: function TestParentComponent() { return React.createElement(Outlet); },
    ScreenData: React.createContext(null),
  };
});

jest.mock("./Recquire Authentication/APIs/authenticationAPIs", () => ({
  checkAuthentication: jest.fn(),
}));

jest.mock("axios", () => ({
  create: jest.fn(() => ({ get: jest.fn() })),
}));

jest.mock("./api/provenance/provenanceApi", () => ({
  enums: {
    sourceTypes: ["report"],
    claimStatuses: ["draft", "accepted"],
    allowedStatusTransitions: { draft: ["accepted"], accepted: [] },
    assessmentOutcomes: ["accept", "reject"],
    identityKinds: ["organisation", "person"],
    relationshipTypes: ["founded"],
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
    createClaim: jest.fn(),
    createSource: jest.fn(),
  },
}));

const selectedClaim = {
  id: "claim-route-id",
  status: "draft",
  research_notes: "Route-loaded claim",
  created_at: "2026-10-24T10:00:00Z",
  source_ids: [],
  proposition: { proposition_type: "identity_proposal", identity_kind: "organisation", canonical_name: "Routed claim", aliases: [], attributes: {} },
};

function LocationProbe() {
  const { pathname } = useLocation();
  return <output data-testid="pathname">{pathname}</output>;
}

function HistoryControls() {
  const navigate = useNavigate();
  return (
    <>
      <button onClick={() => navigate(-1)}>History back</button>
      <button onClick={() => navigate(1)}>History forward</button>
    </>
  );
}

function renderApp(initialEntry) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <LocationProbe />
      <HistoryControls />
      <App />
    </MemoryRouter>,
  );
}

function workflowNavigation() {
  return within(screen.getByRole("navigation", { name: "Provenance workflows" }));
}

beforeEach(() => {
  jest.clearAllMocks();
  checkAuthentication.mockResolvedValue({ status: true, user: null });
  provenanceApi.getClaim.mockImplementation(async (claimId) => ({ ...selectedClaim, id: claimId }));
  provenanceApi.getSource.mockResolvedValue({ id: "source-1", title: "Source", source_type: "report" });
  provenanceApi.getAssessments.mockResolvedValue([]);
});

test("redirects the provenance index to the empty review route with review navigation active", async () => {
  renderApp("/provenance");
  expect(await screen.findByRole("heading", { name: "Start with a claim ID" }, { timeout: 5000 })).toBeInTheDocument();
  expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review");
  expect(workflowNavigation().getByRole("link", { name: "Review a claim" })).toHaveClass("active");
  expect(screen.getAllByRole("heading", { name: "Open a claim" })).toHaveLength(1);
  expect(checkAuthentication).toHaveBeenCalledTimes(1);
});

test("renders the claim and source creation routes with only the matched workflow", async () => {
  const { unmount } = renderApp("/provenance/claims/new");
  expect(await screen.findByRole("heading", { name: "Propose a knowledge change" })).toBeInTheDocument();
  expect(workflowNavigation().getByRole("link", { name: "Create claim" })).toHaveClass("active");
  expect(screen.queryByRole("heading", { name: "Add a source" })).not.toBeInTheDocument();
  unmount();

  renderApp("/provenance/sources/new");
  expect(await screen.findByRole("heading", { name: "Add a source" })).toBeInTheDocument();
  expect(workflowNavigation().getByRole("link", { name: "Add a source" })).toHaveClass("active");
  expect(screen.queryByRole("heading", { name: "Propose a knowledge change" })).not.toBeInTheDocument();
});

test("workflow links and browser Back and Forward restore the matched route", async () => {
  renderApp("/provenance/review");
  await screen.findByRole("heading", { name: "Start with a claim ID" });

  fireEvent.click(workflowNavigation().getByRole("link", { name: "Create claim" }));
  expect(await screen.findByRole("heading", { name: "Propose a knowledge change" })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "History back" }));
  expect(await screen.findByRole("heading", { name: "Start with a claim ID" })).toBeInTheDocument();
  expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review");
  fireEvent.click(screen.getByRole("button", { name: "History forward" }));
  expect(await screen.findByRole("heading", { name: "Propose a knowledge change" })).toBeInTheDocument();
  expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/claims/new");
});

test("direct claim routes load the ID and successful manual lookup updates the URL without a second request", async () => {
  const { unmount } = renderApp("/provenance/review/claim-route-id");
  expect(await screen.findByRole("heading", { name: "Routed claim" })).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Claim UUID")).toHaveValue("claim-route-id");
  expect(provenanceApi.getClaim).toHaveBeenCalledTimes(1);
  unmount();

  provenanceApi.getClaim.mockClear();
  renderApp("/provenance/review");
  await screen.findByRole("heading", { name: "Start with a claim ID" });
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: "manual-claim-id" } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("heading", { name: "Routed claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/manual-claim-id"));
  expect(provenanceApi.getClaim).toHaveBeenCalledTimes(1);
});

test("Back and Forward restore different selected claim routes and load their claims", async () => {
  provenanceApi.getClaim.mockImplementation(async (claimId) => ({
    ...selectedClaim,
    id: claimId,
    proposition: { ...selectedClaim.proposition, canonical_name: `Claim ${claimId}` },
  }));
  renderApp("/provenance/review/first-claim");
  expect(await screen.findByRole("heading", { name: "Claim first-claim" })).toBeInTheDocument();

  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: "second-claim" } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("heading", { name: "Claim second-claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/second-claim"));

  fireEvent.click(screen.getByRole("button", { name: "History back" }));
  expect(await screen.findByRole("heading", { name: "Claim first-claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/first-claim"));
  fireEvent.click(screen.getByRole("button", { name: "History forward" }));
  expect(await screen.findByRole("heading", { name: "Claim second-claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/second-claim"));
  expect(provenanceApi.getClaim).toHaveBeenCalledTimes(4);
});

test("Back clears a manually selected claim and Forward restores it", async () => {
  renderApp("/provenance/review");
  await screen.findByRole("heading", { name: "Start with a claim ID" });
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: "selected-claim" } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("heading", { name: "Routed claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/selected-claim"));

  fireEvent.click(screen.getByRole("button", { name: "History back" }));
  expect(await screen.findByRole("heading", { name: "Start with a claim ID" })).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Claim UUID")).toHaveValue("");
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review"));

  fireEvent.click(screen.getByRole("button", { name: "History forward" }));
  expect(await screen.findByRole("heading", { name: "Routed claim" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/selected-claim"));
  expect(provenanceApi.getClaim).toHaveBeenCalledTimes(2);
});

test("failed manual claim lookup leaves the URL on the unselected review route", async () => {
  provenanceApi.getClaim.mockRejectedValueOnce(new Error("Claim was not found."));
  renderApp("/provenance/review");
  await screen.findByRole("heading", { name: "Start with a claim ID" });
  fireEvent.change(screen.getByPlaceholderText("Claim UUID"), { target: { value: "missing-claim" } });
  fireEvent.click(screen.getByRole("button", { name: "Load" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Claim was not found.");
  expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review");
});

test("successful claim creation navigates using the created claim ID", async () => {
  provenanceApi.createClaim.mockResolvedValue({ ...selectedClaim, id: "created-claim-id" });
  renderApp("/provenance/claims/new");
  await screen.findByRole("heading", { name: "Propose a knowledge change" });
  fireEvent.change(screen.getByLabelText(/Canonical name/), { target: { value: "Created entity" } });
  fireEvent.click(screen.getByRole("button", { name: "Create claim" }));

  expect(await screen.findByRole("heading", { name: "Routed claim" })).toBeInTheDocument();
  expect(screen.getByTestId("pathname")).toHaveTextContent("/provenance/review/created-claim-id");
  expect(provenanceApi.createClaim).toHaveBeenCalledTimes(1);
  expect(provenanceApi.getClaim).toHaveBeenCalledWith("created-claim-id");
});
