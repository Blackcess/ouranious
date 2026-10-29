import { IdBadge, label, Status } from "./ReviewPrimitives";

export default function ClaimDetails({ claim }) {
  return (
    <>
      <div className="prov-claim-heading">
        <div>
          <p className="prov-eyebrow">CLAIM · {label(claim.proposition.proposition_type)}</p>
          <h2>{claim.proposition.canonical_name || claim.proposition.attribute_name || claim.proposition.relationship_type || claim.proposition.property_name || "Claim detail"}</h2>
        </div>
        <Status value={claim.status} />
      </div>
      <dl className="prov-meta">
        <dt>Claim ID</dt><dd><IdBadge value={claim.id} /></dd>
        <dt>Created</dt><dd>{new Date(claim.created_at).toLocaleString()}</dd>
        <dt>Research notes</dt><dd>{claim.research_notes || <em>No notes recorded</em>}</dd>
      </dl>
      <div className="prov-subpanel">
        <h3>Proposition</h3>
        <pre>{JSON.stringify(claim.proposition, null, 2)}</pre>
      </div>
    </>
  );
}
