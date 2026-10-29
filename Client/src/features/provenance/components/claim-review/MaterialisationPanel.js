import { IdBadge, label, Status } from "./ReviewPrimitives";

function MaterialisationResult({ result }) {
  const summary = result.action === "created"
    ? "Created a new record"
    : result.action === "linked"
      ? "Linked to an existing record"
      : result.already_materialised
        ? "Claim was already materialised"
        : result.action === null
          ? "Resolution blocked"
          : label(result.action);

  return (
    <div className={`prov-materialisation ${result.action === null ? "is-blocked" : ""}`}>
      <div className="prov-result-head">
        <strong>{summary}</strong>
        <Status value={result.outcome} />
      </div>
      <p>Target kind: {label(result.target_kind)} · Action: {result.action ? label(result.action) : "None"}</p>
      {result.target_id ? <p>Target ID: <IdBadge value={result.target_id} /></p> : <p className="prov-muted">No target ID was returned.</p>}
      {result.override_applied && <p className="prov-hint">Possible duplicate override was applied.</p>}
      {result.candidates_truncated && <p className="prov-notice notice-warning">Candidate list is truncated; additional matches may exist.</p>}
      {result.candidates?.length > 0 && (
        <div className="prov-candidates">
          <h3>Candidate matches</h3>
          {result.candidates.map((candidate) => (
            <article key={candidate.id}>
              <strong>{candidate.canonical_name || label(candidate.relationship_type)}</strong>
              <span>{candidate.kind ? label(candidate.kind) : "Relationship"} · {label(candidate.match_kind || "match")}</span>
              <IdBadge value={candidate.id} />
              <details>
                <summary>Evidence and details</summary>
                <pre>{JSON.stringify(candidate, null, 2)}</pre>
              </details>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default function MaterialisationPanel({
  allowDuplicate,
  materialisation,
  materialisationLoading,
  onAllowDuplicateChange,
  onMaterialise,
}) {
  const confirmAndMaterialise = () => {
    if (window.confirm("Materialise this claim? This may create or link an identity or relationship.")) {
      onMaterialise();
    }
  };

  return (
    <section className="prov-panel">
      <p className="prov-eyebrow">RESOLUTION</p>
      <h2>Materialise claim</h2>
      <p className="prov-muted">The server decides whether this creates a new record, links to an existing one, or blocks resolution.</p>
      <label className="prov-check">
        <input type="checkbox" checked={allowDuplicate} onChange={(event) => onAllowDuplicateChange(event.target.checked)} />
        Allow possible duplicate
      </label>
      <p className="prov-hint">This requests the server’s duplicate override behavior. It does not select a candidate.</p>
      <button className="prov-primary prov-danger" disabled={materialisationLoading} onClick={confirmAndMaterialise}>
        {materialisationLoading ? "Resolving…" : "Run materialisation"}
      </button>
      {materialisation && <MaterialisationResult result={materialisation} />}
    </section>
  );
}
