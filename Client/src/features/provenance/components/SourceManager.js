import { useState } from "react";
import { enums, provenanceApi } from "../../../api/provenance/provenanceApi";
import { getErrorMessage } from "../../../api/provenance/errors";

const label = (value = "") => value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());

const initialSourceForm = {
  title: "",
  source_type: "official_website",
  publisher: "",
  url: "",
  publication_date: "",
};

function Field({ title, required, children }) {
  return (
    <label className="prov-field">
      <span>
        {title}
        {required && <b aria-label="required"> *</b>}
      </span>
      {children}
    </label>
  );
}

function SourceTypeSelect({ value, onChange }) {
  return (
    <select value={value} onChange={onChange}>
      {enums.sourceTypes.map((sourceType) => (
        <option key={sourceType} value={sourceType}>
          {label(sourceType)}
        </option>
      ))}
    </select>
  );
}

function SourceId({ value }) {
  const [copied, setCopied] = useState(false);

  const copyId = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      // Clipboard access is optional; the ID remains visible for manual copying.
    }
  };

  return (
    <span className="prov-id">
      <code title={value}>{value}</code>
      <button type="button" className="prov-copy" onClick={copyId} aria-label="Copy ID">
        {copied ? "Copied" : "Copy"}
      </button>
    </span>
  );
}

function SourceDetails({ source }) {
  return (
    <div className="prov-source-detail">
      <h3>Source created</h3>
      <p>
        <strong>{source.title}</strong> · {label(source.source_type)}
      </p>
      <dl className="prov-meta">
        <dt>ID</dt>
        <dd><SourceId value={source.id} /></dd>
        <dt>Publisher</dt>
        <dd>{source.publisher || "—"}</dd>
        <dt>Published</dt>
        <dd>{source.publication_date || "—"}</dd>
        <dt>Retrieved</dt>
        <dd>{new Date(source.retrieved_at).toLocaleString()}</dd>
        <dt>URL</dt>
        <dd>
          {source.url ? (
            <a href={source.url} target="_blank" rel="noreferrer">{source.url}</a>
          ) : "—"}
        </dd>
      </dl>
    </div>
  );
}

export default function SourceManager() {

  const [sourceForm, setSourceForm] = useState(initialSourceForm);
  const [sourceId, setSourceId] = useState("");
  const [source, setSource] = useState(null);
  const [creating, setCreating] = useState(false);
  const [retrieving, setRetrieving] = useState(false);
  const [notice, setNotice] = useState(null);

  const createSource = async (event) => {
    event.preventDefault();
    if (creating) return;

    setCreating(true);
    setNotice(null);
    try {
      const created = await provenanceApi.createSource({
        title: sourceForm.title.trim(),
        source_type: sourceForm.source_type,
        publisher: sourceForm.publisher.trim() || null,
        url: sourceForm.url.trim() || null,
        publication_date: sourceForm.publication_date || null,
      });
      setSource(created);
      setSourceId(created.id);
      setNotice({ kind: "success", text: "Source created." });

      console.log("Created Source Id: ",created.id)
    } catch (error) {
      setNotice({ kind: "error", text: getErrorMessage(error) });
    } finally {
      setCreating(false);
    }
  };

  const retrieveSource = async () => {
    if (retrieving || !sourceId.trim()) return;

    setRetrieving(true);
    setNotice(null);
    try {
      const retrieved = await provenanceApi.getSource(sourceId.trim());
      setSource(retrieved);
    } catch (error) {
      setSource(null);
      setNotice({ kind: "error", text: getErrorMessage(error) });
    } finally {
      setRetrieving(false);
    }
  };

  return (
    <section className="prov-panel">
      <div className="prov-panel-head">
        <div>
          <p className="prov-eyebrow">SOURCE RECORD</p>
          <h2>Add a source</h2>
          <p>Capture where information came from. Retrieval time is assigned by the API.</p>
        </div>
      </div>

      {notice && (
        <div className={`prov-notice notice-${notice.kind}`} role="status">
          {notice.text}
        </div>
      )}

      <form onSubmit={createSource} className="prov-form-grid">
        <Field title="Title" required>
          <input
            required
            minLength="1"
            value={sourceForm.title}
            onChange={(event) => setSourceForm({ ...sourceForm, title: event.target.value })}
            placeholder="Source or publication title"
          />
        </Field>
        <Field title="Source type" required>
          <SourceTypeSelect
            value={sourceForm.source_type}
            onChange={(event) => setSourceForm({ ...sourceForm, source_type: event.target.value })}
          />
        </Field>
        <Field title="Publisher">
          <input
            value={sourceForm.publisher}
            onChange={(event) => setSourceForm({ ...sourceForm, publisher: event.target.value })}
          />
        </Field>
        <Field title="URL">
          <input
            type="url"
            value={sourceForm.url}
            onChange={(event) => setSourceForm({ ...sourceForm, url: event.target.value })}
            placeholder="https://"
          />
        </Field>
        <Field title="Publication date">
          <input
            type="date"
            value={sourceForm.publication_date}
            onChange={(event) => setSourceForm({ ...sourceForm, publication_date: event.target.value })}
          />
        </Field>
        <div className="prov-actions">
          <button className="prov-primary" disabled={creating}>
            {creating ? "Saving…" : "Create source"}
          </button>
        </div>
      </form>

      <div className="prov-divider" />
      <div className="prov-inline-form">
        <Field title="Retrieve source by ID">
          <input
            value={sourceId}
            onChange={(event) => setSourceId(event.target.value)}
            placeholder="Source UUID"
          />
        </Field>
        <button
          type="button"
          className="prov-secondary"
          disabled={retrieving || !sourceId.trim()}
          onClick={retrieveSource}
        >
          {retrieving ? "Retrieving…" : "Retrieve"}
        </button>
      </div>

      {source && <SourceDetails source={source} />}
    </section>
  );
}
