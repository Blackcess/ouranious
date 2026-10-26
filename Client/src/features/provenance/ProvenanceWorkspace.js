import { useEffect, useMemo, useState } from "react";
import { enums, provenanceApi } from "../../api/provenance/provenanceApi";
import { getErrorMessage } from "../../api/provenance/errors";
import { parseJsonValue } from "../../api/provenance/typedValueCodec";
import { relationshipPropertySchemas } from "../../api/provenance/relationshipSchemas";
import "./provenance.css";

const label = (value = "") => value.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
const initialProposition = { proposition_type: "identity_proposal", identity_kind: "organisation", canonical_name: "", aliases: "", attributes: "{}", source_ids: "" };

function Field({ title, required, hint, children }) {
  return <label className="prov-field"><span>{title}{required && <b aria-label="required"> *</b>}</span>{children}{hint && <small>{hint}</small>}</label>;
}
function Select({ value, onChange, options }) { return <select value={value} onChange={onChange}>{options.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>; }
function JsonField({ title, value, onChange, hint }) { return <Field title={title} hint={hint}><textarea rows="5" value={value} onChange={onChange} spellCheck="false" /></Field>; }
function IdBadge({ value }) {
  const [copied, setCopied] = useState(false);
  return <span className="prov-id"><code title={value}>{value}</code><button type="button" className="prov-copy" onClick={async () => { try { await navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 1200); } catch {} }} aria-label="Copy ID">{copied ? "Copied" : "Copy"}</button></span>;
}
function Status({ value }) { return <span className={`prov-status status-${value}`}>{label(value)}</span>; }

export default function ProvenanceWorkspace() {
  const [section, setSection] = useState("review");
  const [notice, setNotice] = useState(null);
  const [busy, setBusy] = useState(false);
  const [sourceId, setSourceId] = useState("");
  const [source, setSource] = useState(null);
  const [claimIdInput, setClaimIdInput] = useState("");
  const [claim, setClaim] = useState(null);
  const [sourceRecords, setSourceRecords] = useState({});
  const [assessments, setAssessments] = useState([]);
  const [materialisation, setMaterialisation] = useState(null);
  const [sourceForm, setSourceForm] = useState({ title: "", source_type: "official_website", publisher: "", url: "", publication_date: "" });
  const [claimForm, setClaimForm] = useState({ ...initialProposition, research_notes: "" });
  const [assessmentForm, setAssessmentForm] = useState({ outcome: "accept", rationale: "", assessed_by: "", review_process: "", transition_claim_to: "" });
  const [associationId, setAssociationId] = useState("");
  const [statusTarget, setStatusTarget] = useState("");
  const [allowDuplicate, setAllowDuplicate] = useState(false);

  const proposition = useMemo(() => {
    try {
    const p = { proposition_type: claimForm.proposition_type };
    if (p.proposition_type === "identity_attribute") Object.assign(p, { identity_id: claimForm.identity_id || "", attribute_name: claimForm.attribute_name || "", proposed_value: parseJsonValue(claimForm.proposed_value || "null", "Proposed value") });
    if (p.proposition_type === "relationship") Object.assign(p, { source_identity_id: claimForm.source_identity_id || "", target_identity_id: claimForm.target_identity_id || "", relationship_type: claimForm.relationship_type || "founded", existing_relationship_id: claimForm.existing_relationship_id || null, properties: parseJsonValue(claimForm.properties || "null", "Properties") });
    if (p.proposition_type === "relationship_property") Object.assign(p, { relationship_id: claimForm.relationship_id || "", property_name: claimForm.property_name || "", proposed_value: parseJsonValue(claimForm.proposed_value || "null", "Proposed value") });
    if (p.proposition_type === "identity_proposal") Object.assign(p, { identity_kind: claimForm.identity_kind || "organisation", canonical_name: claimForm.canonical_name || "", aliases: (claimForm.aliases || "").split("\n").map((v) => v.trim()).filter(Boolean), attributes: parseJsonValue(claimForm.attributes || "{}", "Attributes") });
    return p;
    } catch { return null; }
  }, [claimForm]);

  useEffect(() => { setNotice(null); }, [section]);
  const run = async (work, successMessage) => {
    setBusy(true); setNotice(null);
    try { const result = await work(); if (successMessage) setNotice({ kind: "success", text: successMessage }); return result; }
    catch (error) { setNotice({ kind: "error", text: getErrorMessage(error) }); return null; }
    finally { setBusy(false); }
  };
  const loadClaim = async (id) => {
    const loaded = await run(async () => {
      const found = await provenanceApi.getClaim(id);
      const sources = await Promise.all(found.source_ids.map(async (sourceId) => {
        try { return [sourceId, await provenanceApi.getSource(sourceId)]; }
        catch { return [sourceId, null]; }
      }));
      return { found, sources: Object.fromEntries(sources) };
    });
    if (!loaded) return;
    const { found } = loaded;
    setSourceRecords(loaded.sources);
    setClaim(found); setClaimIdInput(found.id); setMaterialisation(null);
    setAssessments([]);
    const history = await run(() => provenanceApi.getAssessments(found.id));
    if (history) setAssessments(history);
  };
  const updateForm = (key, value) => setClaimForm((prev) => ({ ...prev, [key]: value }));
  const createSource = async (event) => {
    event.preventDefault();
    const created = await run(() => provenanceApi.createSource({ title: sourceForm.title.trim(), source_type: sourceForm.source_type, publisher: sourceForm.publisher.trim() || null, url: sourceForm.url.trim() || null, publication_date: sourceForm.publication_date || null }), "Source created.");
    if (created) { setSource(created); setSourceId(created.id); }
  };
  const createClaim = async (event) => {
    event.preventDefault();
    const sourceIds = (claimForm.source_ids || "").split(/[\n,]/).map((v) => v.trim()).filter(Boolean);
    const created = await run(() => provenanceApi.createClaim({ proposition, source_ids: sourceIds, research_notes: claimForm.research_notes || "" }), "Claim created.");
    if (created) { setClaim(created); setClaimIdInput(created.id); setAssessments([]); setSection("review"); }
    console.log("Created Claim: ", created)
  };
  const handleMaterialise = async () => {
    if (!window.confirm("Materialise this claim? This may create or link an identity or relationship.")) return;
    const result = await run(() => provenanceApi.materialise(claim.id, allowDuplicate));
    if (result) { setMaterialisation(result.data); setNotice({ kind: result.status === 409 ? "warning" : "success", text: result.status === 409 ? "Resolution was blocked. Review the candidates and claim data." : `Materialisation response: HTTP ${result.status}.` }); }
  };

  return <main className="prov-shell">
    <header className="prov-header"><div><p className="prov-eyebrow">OURANIOUS · KNOWLEDGE BASE</p><h1>Provenance workspace</h1><p>Record sources, propose claims, review evidence, and track resolution.</p></div><div className="prov-api"><span className="prov-live-dot" />API configured <code>/api/v1</code></div></header>
    <nav className="prov-tabs" aria-label="Provenance workflows">
      {[ ["review", "Review a claim"], ["claim", "Create claim"], ["source", "Add a source"] ].map(([key, text]) => <button type="button" key={key} className={section === key ? "active" : ""} onClick={() => setSection(key)}>{text}</button>)}
    </nav>
    {notice && <div className={`prov-notice notice-${notice.kind}`} role="status">{notice.text}</div>}
    {section === "source" && <section className="prov-panel"><div className="prov-panel-head"><div><p className="prov-eyebrow">SOURCE RECORD</p><h2>Add a source</h2><p>Capture where information came from. Retrieval time is assigned by the API.</p></div></div>
      <form onSubmit={createSource} className="prov-form-grid">
        <Field title="Title" required><input required minLength="1" value={sourceForm.title} onChange={(e) => setSourceForm({ ...sourceForm, title: e.target.value })} placeholder="Source or publication title" /></Field>
        <Field title="Source type" required><Select value={sourceForm.source_type} options={enums.sourceTypes} onChange={(e) => setSourceForm({ ...sourceForm, source_type: e.target.value })} /></Field>
        <Field title="Publisher"><input value={sourceForm.publisher} onChange={(e) => setSourceForm({ ...sourceForm, publisher: e.target.value })} /></Field>
        <Field title="URL"><input type="url" value={sourceForm.url} onChange={(e) => setSourceForm({ ...sourceForm, url: e.target.value })} placeholder="https://" /></Field>
        <Field title="Publication date"><input type="date" value={sourceForm.publication_date} onChange={(e) => setSourceForm({ ...sourceForm, publication_date: e.target.value })} /></Field>
        <div className="prov-actions"><button className="prov-primary" disabled={busy}>{busy ? "Saving…" : "Create source"}</button></div>
      </form>
      <div className="prov-divider" /><div className="prov-inline-form"><Field title="Retrieve source by ID"><input value={sourceId} onChange={(e) => setSourceId(e.target.value)} placeholder="Source UUID" /></Field><button className="prov-secondary" disabled={busy || !sourceId.trim()} onClick={() => run(() => provenanceApi.getSource(sourceId.trim())).then(setSource)}>Retrieve</button></div>
      {source && <SourceDetails source={source} />}
    </section>}
    {section === "claim" && <section className="prov-panel"><div className="prov-panel-head"><div><p className="prov-eyebrow">NEW CLAIM</p><h2>Propose a knowledge change</h2><p>Use the exact identifiers you already know. This API has no identity or source search endpoint.</p></div></div>
      <form onSubmit={createClaim} className="prov-form-grid">
        <Field title="Proposition type" required><Select value={claimForm.proposition_type} options={["identity_proposal", "identity_attribute", "relationship", "relationship_property"]} onChange={(e) => setClaimForm({ ...initialProposition, research_notes: claimForm.research_notes, proposition_type: e.target.value })} /></Field>
        {claimForm.proposition_type === "identity_proposal" && <>
          <Field title="Identity kind" required><Select value={claimForm.identity_kind} options={enums.identityKinds} onChange={(e) => updateForm("identity_kind", e.target.value)} /></Field>
          <Field title="Canonical name" required><input required value={claimForm.canonical_name || ""} onChange={(e) => updateForm("canonical_name", e.target.value)} /></Field>
          <Field title="Aliases" hint="One alias per line"><textarea rows="3" value={claimForm.aliases || ""} onChange={(e) => updateForm("aliases", e.target.value)} /></Field>
          <JsonField title="Attributes (JSON object)" value={claimForm.attributes || "{}"} onChange={(e) => updateForm("attributes", e.target.value)} hint="Use ordinary JSON values; the API decodes supported tagged values." />
        </>}
        {claimForm.proposition_type === "identity_attribute" && <>
          <Field title="Identity UUID" required><input required value={claimForm.identity_id || ""} onChange={(e) => updateForm("identity_id", e.target.value)} /></Field>
          <Field title="Attribute name" required><input required value={claimForm.attribute_name || ""} onChange={(e) => updateForm("attribute_name", e.target.value)} /></Field>
          <JsonField title="Proposed value (JSON)" value={claimForm.proposed_value || '""'} onChange={(e) => updateForm("proposed_value", e.target.value)} />
        </>}
        {claimForm.proposition_type === "relationship" && <>
          <Field title="Source identity UUID" required><input required value={claimForm.source_identity_id || ""} onChange={(e) => updateForm("source_identity_id", e.target.value)} /></Field>
          <Field title="Target identity UUID" required><input required value={claimForm.target_identity_id || ""} onChange={(e) => updateForm("target_identity_id", e.target.value)} /></Field>
          <Field title="Relationship type" required><Select value={claimForm.relationship_type || "founded"} options={enums.relationshipTypes} onChange={(e) => updateForm("relationship_type", e.target.value)} /></Field>
          <Field title="Existing relationship UUID"><input value={claimForm.existing_relationship_id || ""} onChange={(e) => updateForm("existing_relationship_id", e.target.value)} /></Field>
          <JsonField title="Relationship properties (JSON)" value={claimForm.properties || "null"} onChange={(e) => updateForm("properties", e.target.value)} hint={relationshipPropertySchemas[claimForm.relationship_type || "founded"].length ? `Allowed fields: ${relationshipPropertySchemas[claimForm.relationship_type || "founded"].join(", ")}. All are optional; date and enum values are checked by the API.` : "This relationship type accepts no properties; use null or {}."} />
        </>}
        {claimForm.proposition_type === "relationship_property" && <>
          <Field title="Relationship UUID" required><input required value={claimForm.relationship_id || ""} onChange={(e) => updateForm("relationship_id", e.target.value)} /></Field>
          <Field title="Property name" required><input required value={claimForm.property_name || ""} onChange={(e) => updateForm("property_name", e.target.value)} /></Field>
          <JsonField title="Proposed value (JSON)" value={claimForm.proposed_value || '""'} onChange={(e) => updateForm("proposed_value", e.target.value)} />
        </>}
        <div className="prov-full"><Field title="Existing source UUIDs" hint="Optional; separate UUIDs with commas or new lines. Sources can also be attached after creation."><textarea rows="2" value={claimForm.source_ids || ""} onChange={(e) => updateForm("source_ids", e.target.value)} placeholder="UUID, UUID" /></Field></div>
        <div className="prov-full"><Field title="Research notes"><textarea rows="4" value={claimForm.research_notes} onChange={(e) => updateForm("research_notes", e.target.value)} placeholder="Context, caveats, and what should be verified" /></Field></div>
        <div className="prov-full prov-preview"><span>Review payload</span>{!proposition && <p className="prov-validation">Enter valid JSON in the value fields.</p>}<pre>{JSON.stringify({ proposition, source_ids: (claimForm.source_ids || "").split(/[\n,]/).map((v) => v.trim()).filter(Boolean), research_notes: claimForm.research_notes || "" }, null, 2)}</pre></div>
        <div className="prov-actions"><button className="prov-primary" disabled={busy || !proposition || !propositionReady(proposition)}>{busy ? "Submitting…" : "Create claim"}</button></div>
      </form>
    </section>}
    {section === "review" && <section className="prov-review-layout"><div className="prov-panel prov-lookup"><p className="prov-eyebrow">CLAIM REVIEW</p><h2>Open a claim</h2><div className="prov-inline-form"><Field title="Claim UUID"><input value={claimIdInput} onChange={(e) => setClaimIdInput(e.target.value)} placeholder="Claim UUID" /></Field><button className="prov-primary" disabled={busy || !claimIdInput.trim()} onClick={() => loadClaim(claimIdInput.trim())}>{busy ? "Loading…" : "Load"}</button></div></div>
      {claim ? <>
        <section className="prov-panel"><div className="prov-claim-heading"><div><p className="prov-eyebrow">CLAIM · {label(claim.proposition.proposition_type)}</p><h2>{claim.proposition.canonical_name || claim.proposition.attribute_name || claim.proposition.relationship_type || claim.proposition.property_name || "Claim detail"}</h2></div><Status value={claim.status} /></div>
          <dl className="prov-meta"><dt>Claim ID</dt><dd><IdBadge value={claim.id} /></dd><dt>Created</dt><dd>{new Date(claim.created_at).toLocaleString()}</dd><dt>Research notes</dt><dd>{claim.research_notes || <em>No notes recorded</em>}</dd></dl>
          <div className="prov-subpanel"><h3>Proposition</h3><pre>{JSON.stringify(claim.proposition, null, 2)}</pre></div>
          <div className="prov-subpanel"><h3>Sources <span className="prov-count">{claim.source_ids.length}</span></h3>{claim.source_ids.length ? <ul className="prov-source-list">{claim.source_ids.map((sid) => { const source = sourceRecords[sid]; return <li key={sid}><div className="prov-associated-source">{source ? <><strong>{source.title}</strong><span>{label(source.source_type)}{source.publisher ? ` · ${source.publisher}` : ""}{source.publication_date ? ` · Published ${source.publication_date}` : ""}</span></> : <span className="prov-muted">Source details unavailable</span>}<IdBadge value={sid} /></div><button className="prov-text-button" disabled={busy} onClick={() => run(() => provenanceApi.removeSource(claim.id, sid), "Source detached.").then((r) => r && loadClaim(claim.id))}>Remove</button></li>; })}</ul> : <p className="prov-muted">No sources attached yet.</p>}
            <div className="prov-inline-form"><Field title="Attach existing source UUID"><input value={associationId} onChange={(e) => setAssociationId(e.target.value)} placeholder="Source UUID" /></Field><button className="prov-secondary" disabled={busy || !associationId.trim()} onClick={() => run(() => provenanceApi.addSource(claim.id, associationId.trim()), "Source attached.").then((r) => r && loadClaim(claim.id))}>Attach source</button></div>
          </div>
          <div className="prov-subpanel"><h3>Claim status</h3><div className="prov-inline-form"><Field title="Transition to"><select value={statusTarget} onChange={(e) => setStatusTarget(e.target.value)}><option value="">Choose a valid transition</option>{(enums.allowedStatusTransitions[claim.status] || []).map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></Field><button className="prov-secondary" disabled={busy || !statusTarget} onClick={() => run(() => provenanceApi.updateClaimStatus(claim.id, statusTarget), "Claim status updated.").then((next) => { if (next) { setClaim(next); setStatusTarget(""); } })}>Update status</button></div><p className="prov-hint">Available transitions mirror the current domain rules; the API remains authoritative.</p></div>
        </section>
        <div className="prov-two-col">
          <section className="prov-panel"><p className="prov-eyebrow">VERIFICATION</p><h2>Record assessment</h2><form onSubmit={(e) => { e.preventDefault(); run(() => provenanceApi.createAssessment(claim.id, { ...assessmentForm, transition_claim_to: assessmentForm.transition_claim_to || null, review_process: assessmentForm.review_process || null }), "Assessment recorded.").then((created) => { if (!created) return; if (created.claim_status) setClaim((old) => ({ ...old, status: created.claim_status })); setAssessments((old) => [created.assessment, ...old]); setAssessmentForm({ outcome: "accept", rationale: "", assessed_by: "", review_process: "", transition_claim_to: "" }); }); }} className="prov-stack">
            <Field title="Outcome" required><Select value={assessmentForm.outcome} options={enums.assessmentOutcomes} onChange={(e) => setAssessmentForm({ ...assessmentForm, outcome: e.target.value })} /></Field>
            <Field title="Rationale" required><textarea required minLength="1" value={assessmentForm.rationale} onChange={(e) => setAssessmentForm({ ...assessmentForm, rationale: e.target.value })} /></Field>
            <Field title="Assessed by" required><input required value={assessmentForm.assessed_by} onChange={(e) => setAssessmentForm({ ...assessmentForm, assessed_by: e.target.value })} /></Field>
            <Field title="Review process"><input value={assessmentForm.review_process} onChange={(e) => setAssessmentForm({ ...assessmentForm, review_process: e.target.value })} /></Field>
            <Field title="Also transition claim status"><select value={assessmentForm.transition_claim_to} onChange={(e) => setAssessmentForm({ ...assessmentForm, transition_claim_to: e.target.value })}><option value="">No status transition</option>{(enums.allowedStatusTransitions[claim.status] || []).map((v) => <option key={v} value={v}>{label(v)}</option>)}</select></Field>
            <button className="prov-primary" disabled={busy}>{busy ? "Saving…" : "Record assessment"}</button>
          </form></section>
          <section className="prov-panel"><p className="prov-eyebrow">RESOLUTION</p><h2>Materialise claim</h2><p className="prov-muted">The server decides whether this creates a new record, links to an existing one, or blocks resolution.</p><label className="prov-check"><input type="checkbox" checked={allowDuplicate} onChange={(e) => setAllowDuplicate(e.target.checked)} /> Allow possible duplicate</label><p className="prov-hint">This requests the server’s duplicate override behavior. It does not select a candidate.</p><button className="prov-primary prov-danger" disabled={busy} onClick={handleMaterialise}>{busy ? "Resolving…" : "Run materialisation"}</button>{materialisation && <MaterialisationResult result={materialisation} />}</section>
        </div>
        <section className="prov-panel"><div className="prov-panel-head"><div><p className="prov-eyebrow">AUDIT TRAIL</p><h2>Assessment history <span className="prov-count">{assessments.length}</span></h2></div><button className="prov-secondary" disabled={busy} onClick={() => run(() => provenanceApi.getAssessments(claim.id)).then((rows) => rows && setAssessments(rows))}>Refresh history</button></div>{assessments.length ? <div className="prov-assessment-list">{assessments.map((record) => <article key={record.id}><div className="prov-claim-heading"><Status value={record.outcome} /><time>{new Date(record.assessed_at).toLocaleString()}</time></div><p>{record.rationale}</p><small>Assessed by {record.assessed_by}{record.review_process ? ` · ${record.review_process}` : ""}</small><IdBadge value={record.id} /></article>)}</div> : <p className="prov-muted">No assessments recorded.</p>}</section>
      </> : <div className="prov-empty"><span>◎</span><h2>Start with a claim ID</h2><p>Load a claim to inspect its evidence, assessment history, and materialisation state.</p></div>}
    </section>}
  </main>;
}

function propositionReady(p) {
  if (!p) return false;
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (p.proposition_type === "identity_proposal") return Boolean(p.canonical_name.trim());
  if (p.proposition_type === "identity_attribute") return uuid.test(p.identity_id) && Boolean(p.attribute_name.trim());
  if (p.proposition_type === "relationship") return uuid.test(p.source_identity_id) && uuid.test(p.target_identity_id);
  return uuid.test(p.relationship_id) && Boolean(p.property_name.trim());
}
function SourceDetails({ source }) { return <div className="prov-source-detail"><h3>Source created</h3><p><strong>{source.title}</strong> · {label(source.source_type)}</p><dl className="prov-meta"><dt>ID</dt><dd><IdBadge value={source.id} /></dd><dt>Publisher</dt><dd>{source.publisher || "—"}</dd><dt>Published</dt><dd>{source.publication_date || "—"}</dd><dt>Retrieved</dt><dd>{new Date(source.retrieved_at).toLocaleString()}</dd><dt>URL</dt><dd>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.url}</a> : "—"}</dd></dl></div>; }
function MaterialisationResult({ result }) {
  const summary = result.action === "created" ? "Created a new record" : result.action === "linked" ? "Linked to an existing record" : result.already_materialised ? "Claim was already materialised" : result.action === null ? "Resolution blocked" : label(result.action);
  return <div className={`prov-materialisation ${result.action === null ? "is-blocked" : ""}`}><div className="prov-result-head"><strong>{summary}</strong><Status value={result.outcome} /></div><p>Target kind: {label(result.target_kind)} · Action: {result.action ? label(result.action) : "None"}</p>{result.target_id ? <p>Target ID: <IdBadge value={result.target_id} /></p> : <p className="prov-muted">No target ID was returned.</p>}{result.override_applied && <p className="prov-hint">Possible duplicate override was applied.</p>}{result.candidates_truncated && <p className="prov-notice notice-warning">Candidate list is truncated; additional matches may exist.</p>}{result.candidates?.length > 0 && <div className="prov-candidates"><h3>Candidate matches</h3>{result.candidates.map((candidate) => <article key={candidate.id}><strong>{candidate.canonical_name || label(candidate.relationship_type)}</strong><span>{candidate.kind ? label(candidate.kind) : "Relationship"} · {label(candidate.match_kind || "match")}</span><IdBadge value={candidate.id} /><details><summary>Evidence and details</summary><pre>{JSON.stringify(candidate, null, 2)}</pre></details></article>)}</div>}</div>;
}
