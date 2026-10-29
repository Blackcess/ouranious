import { Field, IdBadge, label } from "./ReviewPrimitives";

export default function ClaimSources({
  claim,
  sourceRecords,
  sourcesLoading,
  sourcesError,
  associationId,
  associationLoading,
  onAssociationIdChange,
  onAttachSource,
  onRemoveSource,
}) {
  return (
    <div className="prov-subpanel">
      <h3>Sources <span className="prov-count">{claim.source_ids.length}</span></h3>
      {sourcesLoading && <p className="prov-muted">Loading source details…</p>}
      {sourcesError && <p className="prov-notice notice-error" role="alert">{sourcesError}</p>}
      {claim.source_ids.length ? (
        <ul className="prov-source-list">
          {claim.source_ids.map((sourceId) => {
            const source = sourceRecords[sourceId];
            return (
              <li key={sourceId}>
                <div className="prov-associated-source">
                  {source ? (
                    <>
                      <strong>{source.title}</strong>
                      <span>{label(source.source_type)}{source.publisher ? ` · ${source.publisher}` : ""}{source.publication_date ? ` · Published ${source.publication_date}` : ""}</span>
                    </>
                  ) : (
                    <span className="prov-muted">Source details unavailable</span>
                  )}
                  <IdBadge value={sourceId} />
                </div>
                <button className="prov-text-button" disabled={associationLoading} onClick={() => onRemoveSource(sourceId)}>Remove</button>
              </li>
            );
          })}
        </ul>
      ) : (
        !sourcesLoading && <p className="prov-muted">No sources attached yet.</p>
      )}
      <div className="prov-inline-form">
        <Field title="Attach existing source UUID">
          <input value={associationId} onChange={(event) => onAssociationIdChange(event.target.value)} placeholder="Source UUID" />
        </Field>
        <button className="prov-secondary" disabled={associationLoading || !associationId.trim()} onClick={() => onAttachSource(associationId.trim())}>
          {associationLoading ? "Saving…" : "Attach source"}
        </button>
      </div>
    </div>
  );
}
