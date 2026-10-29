import { enums } from "../../../../api/provenance/provenanceApi";
import { Field, Select } from "./ReviewPrimitives";

export default function AssessmentPanel({
  claim,
  assessmentForm,
  assessmentSubmitting,
  onAssessmentFormChange,
  onSubmit,
}) {
  return (
    <section className="prov-panel">
      <p className="prov-eyebrow">VERIFICATION</p>
      <h2>Record assessment</h2>
      <form onSubmit={onSubmit} className="prov-stack">
        <Field title="Outcome">
          <Select value={assessmentForm.outcome} options={enums.assessmentOutcomes} onChange={(event) => onAssessmentFormChange("outcome", event.target.value)} />
        </Field>
        <Field title="Rationale">
          <textarea required minLength="1" value={assessmentForm.rationale} onChange={(event) => onAssessmentFormChange("rationale", event.target.value)} />
        </Field>
        <Field title="Assessed by">
          <input required value={assessmentForm.assessed_by} onChange={(event) => onAssessmentFormChange("assessed_by", event.target.value)} />
        </Field>
        <Field title="Review process">
          <input value={assessmentForm.review_process} onChange={(event) => onAssessmentFormChange("review_process", event.target.value)} />
        </Field>
        <Field title="Also transition claim status">
          <select value={assessmentForm.transition_claim_to} onChange={(event) => onAssessmentFormChange("transition_claim_to", event.target.value)}>
            <option value="">No status transition</option>
            {(enums.allowedStatusTransitions[claim.status] || []).map((status) => (
              <option key={status} value={status}>{status.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase())}</option>
            ))}
          </select>
        </Field>
        <button className="prov-primary" disabled={assessmentSubmitting}>
          {assessmentSubmitting ? "Saving…" : "Record assessment"}
        </button>
      </form>
    </section>
  );
}
