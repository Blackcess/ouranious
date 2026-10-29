import { Field } from "./ReviewPrimitives";

export default function ClaimLookup({ claimIdInput, onClaimIdChange, onLookup, loading, disabled }) {
  return (
    <div className="prov-panel prov-lookup">
      <p className="prov-eyebrow">CLAIM REVIEW</p>
      <h2>Open a claim</h2>
      <div className="prov-inline-form">
        <Field title="Claim UUID">
          <input value={claimIdInput} onChange={onClaimIdChange} placeholder="Claim UUID" />
        </Field>
        <button className="prov-primary" disabled={disabled} onClick={onLookup}>
          {loading ? "Loading…" : "Load"}
        </button>
      </div>
    </div>
  );
}
