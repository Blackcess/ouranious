import { Field, label } from "./ReviewPrimitives";

export default function ClaimStatusPanel({
  statusTarget,
  statusLoading,
  allowedTransitions,
  onStatusTargetChange,
  onUpdateStatus,
}) {
  return (
    <div className="prov-subpanel">
      <h3>Claim status</h3>
      <div className="prov-inline-form">
        <Field title="Transition to">
          <select value={statusTarget} onChange={(event) => onStatusTargetChange(event.target.value)}>
            <option value="">Choose a valid transition</option>
            {allowedTransitions.map((status) => (
              <option key={status} value={status}>{label(status)}</option>
            ))}
          </select>
        </Field>
        <button className="prov-secondary" disabled={statusLoading || !statusTarget} onClick={onUpdateStatus}>
          {statusLoading ? "Updating…" : "Update status"}
        </button>
      </div>
      <p className="prov-hint">Available transitions mirror the current domain rules; the API remains authoritative.</p>
    </div>
  );
}
