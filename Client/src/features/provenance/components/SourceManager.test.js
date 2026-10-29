import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import SourceManager from "./SourceManager";
import { provenanceApi } from "../../../api/provenance/provenanceApi";

jest.mock("../../../api/provenance/provenanceApi", () => ({
  enums: { sourceTypes: ["official_website", "report"] },
  provenanceApi: { createSource: jest.fn(), getSource: jest.fn() },
}));

const source = {
  id: "source-123",
  title: "Research report",
  source_type: "report",
  publisher: "Example Publisher",
  url: "https://example.com/report",
  publication_date: "2026-10-20",
  retrieved_at: "2026-10-25T10:00:00Z",
};

beforeEach(() => jest.clearAllMocks());

test("renders source creation and retrieval controls with creation validation", () => {
  render(<SourceManager />);

  expect(screen.getByRole("heading", { name: "Add a source" })).toBeInTheDocument();
  expect(screen.getByLabelText(/Title/)).toBeRequired();
  expect(screen.getByLabelText(/Title/)).toHaveAttribute("minLength", "1");
  expect(screen.getByLabelText(/Source type/)).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Source UUID")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Retrieve" })).toBeDisabled();
});

test("creates a source through the API and displays its confirmation and details", async () => {
  provenanceApi.createSource.mockResolvedValue(source);
  render(<SourceManager />);

  fireEvent.change(screen.getByLabelText(/Title/), { target: { value: "  Research report  " } });
  fireEvent.change(screen.getByLabelText(/Source type/), { target: { value: "report" } });
  fireEvent.change(screen.getByLabelText(/Publisher/), { target: { value: " Example Publisher " } });
  fireEvent.change(screen.getByLabelText(/URL/), { target: { value: " https://example.com/report " } });
  fireEvent.change(screen.getByLabelText(/Publication date/), { target: { value: "2026-10-20" } });
  fireEvent.click(screen.getByRole("button", { name: "Create source" }));

  expect(await screen.findByText("Source created.")).toBeInTheDocument();
  expect(provenanceApi.createSource).toHaveBeenCalledWith({
    title: "Research report",
    source_type: "report",
    publisher: "Example Publisher",
    url: "https://example.com/report",
    publication_date: "2026-10-20",
  });
  expect(screen.getByText("source-123")).toBeInTheDocument();
  expect(screen.getByText("Example Publisher")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: source.url })).toHaveAttribute("href", source.url);
  expect(screen.getByPlaceholderText("Source UUID")).toHaveValue(source.id);
});

test("retrieves and displays a source by the entered ID", async () => {
  provenanceApi.getSource.mockResolvedValue(source);
  render(<SourceManager />);

  fireEvent.change(screen.getByPlaceholderText("Source UUID"), { target: { value: " source-123 " } });
  fireEvent.click(screen.getByRole("button", { name: "Retrieve" }));

  expect(await screen.findByText("Research report")).toBeInTheDocument();
  expect(provenanceApi.getSource).toHaveBeenCalledWith("source-123");
  expect(screen.getByText("Example Publisher")).toBeInTheDocument();
});

test("shows source operation errors and loading states", async () => {
  let finishCreate;
  provenanceApi.createSource.mockImplementation(() => new Promise((resolve) => { finishCreate = resolve; }));
  render(<SourceManager />);

  fireEvent.change(screen.getByLabelText(/Title/), { target: { value: "Report" } });
  fireEvent.click(screen.getByRole("button", { name: "Create source" }));
  expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
  finishCreate(source);
  expect(await screen.findByText("Source created.")).toBeInTheDocument();

  let finishRetrieve;
  provenanceApi.getSource.mockImplementationOnce(() => new Promise((resolve) => { finishRetrieve = resolve; }));
  fireEvent.click(screen.getByRole("button", { name: "Retrieve" }));
  expect(screen.getByRole("button", { name: "Retrieving…" })).toBeDisabled();
  finishRetrieve(source);
  expect(await screen.findByText("Research report")).toBeInTheDocument();

  provenanceApi.getSource.mockRejectedValueOnce(new Error("Source was not found."));
  fireEvent.change(screen.getByPlaceholderText("Source UUID"), { target: { value: "missing-id" } });
  fireEvent.click(screen.getByRole("button", { name: "Retrieve" }));
  expect(await screen.findByText("Source was not found.")).toBeInTheDocument();
  expect(screen.queryByText("Research report")).not.toBeInTheDocument();

  provenanceApi.createSource.mockRejectedValueOnce(new Error("Unable to create source."));
  fireEvent.click(screen.getByRole("button", { name: "Create source" }));
  expect(await screen.findByText("Unable to create source.")).toBeInTheDocument();
});
