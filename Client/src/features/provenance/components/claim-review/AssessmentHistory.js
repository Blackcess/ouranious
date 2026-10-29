import { IdBadge, Status } from "./ReviewPrimitives";

export default function AssessmentHistory({ assessments, assessmentsLoading, assessmentsError, onRefresh }) {
  return (
    <section className="prov-panel">
      <div className="prov-panel-head">
        <div>
          <p className="prov-eyebrow">AUDIT TRAIL</p>
          <h2>Assessment history <span className="prov-count">{assessments.length}</span></h2>
        </div>
        <button className="prov-secondary" disabled={assessmentsLoading} onClick={onRefresh}>
          {assessmentsLoading ? "Loading…" : "Refresh history"}
        </button>
      </div>
      {assessmentsLoading ? (
        <p className="prov-muted">Loading assessment history…</p>
      ) : assessmentsError ? (
        <p className="prov-notice notice-error" role="alert">{assessmentsError}</p>
      ) : assessments.length ? (
        <div className="prov-assessment-list">
          {assessments.map((record) => (
            <article key={record.id}>
              <div className="prov-claim-heading">
                <Status value={record.outcome} />
                <time>{new Date(record.assessed_at).toLocaleString()}</time>
              </div>
              <p>{record.rationale}</p>
              <small>Assessed by {record.assessed_by}{record.review_process ? ` · ${record.review_process}` : ""}</small>
              <IdBadge value={record.id} />
            </article>
          ))}
        </div>
      ) : (
        <p className="prov-muted">No assessments recorded.</p>
      )}
    </section>
  );
}
