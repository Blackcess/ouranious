import { useMemo, useState } from "react";
import { enums, provenanceApi } from "../../../api/provenance/provenanceApi";
import { getErrorMessage } from "../../../api/provenance/errors";
import { parseJsonValue } from "../../../api/provenance/typedValueCodec";
import { relationshipPropertySchemas } from "../../../api/provenance/relationshipSchemas";

const label = (value = "") => value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());

const initialProposition = {
  proposition_type: "identity_proposal",
  identity_kind: "organisation",
  canonical_name: "",
  aliases: "",
  attributes: "{}",
  source_ids: "",
};

const initialClaimForm = { ...initialProposition, research_notes: "" };

function Field({ title, required, hint, children }) {
  return (
    <label className="prov-field">
      <span>
        {title}
        {required && <b aria-label="required"> *</b>}
      </span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={onChange}>
      {options.map((option) => (
        <option key={option} value={option}>{label(option)}</option>
      ))}
    </select>
  );
}

function JsonField({ title, value, onChange, hint }) {
  return (
    <Field title={title} hint={hint}>
      <textarea rows="5" value={value} onChange={onChange} spellCheck="false" />
    </Field>
  );
}

function propositionReady(proposition) {
  if (!proposition) return false;
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (proposition.proposition_type === "identity_proposal") return Boolean(proposition.canonical_name.trim());
  if (proposition.proposition_type === "identity_attribute") {
    return uuid.test(proposition.identity_id) && Boolean(proposition.attribute_name.trim());
  }
  if (proposition.proposition_type === "relationship") {
    return uuid.test(proposition.source_identity_id) && uuid.test(proposition.target_identity_id);
  }
  return uuid.test(proposition.relationship_id) && Boolean(proposition.property_name.trim());
}

export default function ClaimCreator({ onClaimCreated, initialDraft, onDraftPreserved }) {
  const [claimForm, setClaimForm] = useState(() => initialDraft || initialClaimForm);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState(null);

  const proposition = useMemo(() => {
    try {
      const payload = { proposition_type: claimForm.proposition_type };
      if (payload.proposition_type === "identity_attribute") {
        Object.assign(payload, {
          identity_id: claimForm.identity_id || "",
          attribute_name: claimForm.attribute_name || "",
          proposed_value: parseJsonValue(claimForm.proposed_value || "null", "Proposed value"),
        });
      }
      if (payload.proposition_type === "relationship") {
        Object.assign(payload, {
          source_identity_id: claimForm.source_identity_id || "",
          target_identity_id: claimForm.target_identity_id || "",
          relationship_type: claimForm.relationship_type || "founded",
          existing_relationship_id: claimForm.existing_relationship_id || null,
          properties: parseJsonValue(claimForm.properties || "null", "Properties"),
        });
      }
      if (payload.proposition_type === "relationship_property") {
        Object.assign(payload, {
          relationship_id: claimForm.relationship_id || "",
          property_name: claimForm.property_name || "",
          proposed_value: parseJsonValue(claimForm.proposed_value || "null", "Proposed value"),
        });
      }
      if (payload.proposition_type === "identity_proposal") {
        Object.assign(payload, {
          identity_kind: claimForm.identity_kind || "organisation",
          canonical_name: claimForm.canonical_name || "",
          aliases: (claimForm.aliases || "").split("\n").map((value) => value.trim()).filter(Boolean),
          attributes: parseJsonValue(claimForm.attributes || "{}", "Attributes"),
        });
      }
      return payload;
    } catch {
      return null;
    }
  }, [claimForm]);

  const sourceIds = (claimForm.source_ids || "").split(/[\n,]/).map((value) => value.trim()).filter(Boolean);

  const updateForm = (key, value) => {
    setClaimForm((previous) => ({ ...previous, [key]: value }));
  };

  const handlePropositionTypeChange = (event) => {
    setClaimForm({
      ...initialProposition,
      research_notes: claimForm.research_notes,
      proposition_type: event.target.value,
    });
  };

  const createClaim = async (event) => {
    event.preventDefault();
    if (submitting || !proposition || !propositionReady(proposition)) return;

    setSubmitting(true);
    setNotice(null);
    let created;
    try {
      created = await provenanceApi.createClaim({
        proposition,
        source_ids: sourceIds,
        research_notes: claimForm.research_notes || "",
      });
    } catch (error) {
      setNotice({ kind: "error", text: getErrorMessage(error) });
      setSubmitting(false);
      return;
    }

    setNotice({ kind: "success", text: "Claim created." });
    setSubmitting(false);
    onClaimCreated(created);
    onDraftPreserved?.(claimForm);
  };

  return (
    <section className="prov-panel">
      <div className="prov-panel-head">
        <div>
          <p className="prov-eyebrow">NEW CLAIM</p>
          <h2>Propose a knowledge change</h2>
          <p>Use the exact identifiers you already know. This API has no identity or source search endpoint.</p>
        </div>
      </div>

      {notice && (
        <div className={`prov-notice notice-${notice.kind}`} role="status">
          {notice.text}
        </div>
      )}

      <form onSubmit={createClaim} className="prov-form-grid">
        <Field title="Proposition type" required>
          <Select
            value={claimForm.proposition_type}
            options={["identity_proposal", "identity_attribute", "relationship", "relationship_property"]}
            onChange={handlePropositionTypeChange}
          />
        </Field>

        {claimForm.proposition_type === "identity_proposal" && (
          <>
            <Field title="Identity kind" required>
              <Select value={claimForm.identity_kind} options={enums.identityKinds} onChange={(event) => updateForm("identity_kind", event.target.value)} />
            </Field>
            <Field title="Canonical name" required>
              <input required value={claimForm.canonical_name || ""} onChange={(event) => updateForm("canonical_name", event.target.value)} />
            </Field>
            <Field title="Aliases" hint="One alias per line">
              <textarea rows="3" value={claimForm.aliases || ""} onChange={(event) => updateForm("aliases", event.target.value)} />
            </Field>
            <JsonField
              title="Attributes (JSON object)"
              value={claimForm.attributes || "{}"}
              onChange={(event) => updateForm("attributes", event.target.value)}
              hint="Use ordinary JSON values; the API decodes supported tagged values."
            />
          </>
        )}

        {claimForm.proposition_type === "identity_attribute" && (
          <>
            <Field title="Identity UUID" required>
              <input required value={claimForm.identity_id || ""} onChange={(event) => updateForm("identity_id", event.target.value)} />
            </Field>
            <Field title="Attribute name" required>
              <input required value={claimForm.attribute_name || ""} onChange={(event) => updateForm("attribute_name", event.target.value)} />
            </Field>
            <JsonField
              title="Proposed value (JSON)"
              value={claimForm.proposed_value || '""'}
              onChange={(event) => updateForm("proposed_value", event.target.value)}
            />
          </>
        )}

        {claimForm.proposition_type === "relationship" && (
          <>
            <Field title="Source identity UUID" required>
              <input required value={claimForm.source_identity_id || ""} onChange={(event) => updateForm("source_identity_id", event.target.value)} />
            </Field>
            <Field title="Target identity UUID" required>
              <input required value={claimForm.target_identity_id || ""} onChange={(event) => updateForm("target_identity_id", event.target.value)} />
            </Field>
            <Field title="Relationship type" required>
              <Select value={claimForm.relationship_type || "founded"} options={enums.relationshipTypes} onChange={(event) => updateForm("relationship_type", event.target.value)} />
            </Field>
            <Field title="Existing relationship UUID">
              <input value={claimForm.existing_relationship_id || ""} onChange={(event) => updateForm("existing_relationship_id", event.target.value)} />
            </Field>
            <JsonField
              title="Relationship properties (JSON)"
              value={claimForm.properties || "null"}
              onChange={(event) => updateForm("properties", event.target.value)}
              hint={relationshipPropertySchemas[claimForm.relationship_type || "founded"].length
                ? `Allowed fields: ${relationshipPropertySchemas[claimForm.relationship_type || "founded"].join(", ")}. All are optional; date and enum values are checked by the API.`
                : "This relationship type accepts no properties; use null or {}."}
            />
          </>
        )}

        {claimForm.proposition_type === "relationship_property" && (
          <>
            <Field title="Relationship UUID" required>
              <input required value={claimForm.relationship_id || ""} onChange={(event) => updateForm("relationship_id", event.target.value)} />
            </Field>
            <Field title="Property name" required>
              <input required value={claimForm.property_name || ""} onChange={(event) => updateForm("property_name", event.target.value)} />
            </Field>
            <JsonField
              title="Proposed value (JSON)"
              value={claimForm.proposed_value || '""'}
              onChange={(event) => updateForm("proposed_value", event.target.value)}
            />
          </>
        )}

        <div className="prov-full">
          <Field title="Existing source UUIDs" hint="Optional; separate UUIDs with commas or new lines. Sources can also be attached after creation.">
            <textarea rows="2" value={claimForm.source_ids || ""} onChange={(event) => updateForm("source_ids", event.target.value)} placeholder="UUID, UUID" />
          </Field>
        </div>
        <div className="prov-full">
          <Field title="Research notes">
            <textarea rows="4" value={claimForm.research_notes} onChange={(event) => updateForm("research_notes", event.target.value)} placeholder="Context, caveats, and what should be verified" />
          </Field>
        </div>
        <div className="prov-full prov-preview">
          <span>Review payload</span>
          {!proposition && <p className="prov-validation">Enter valid JSON in the value fields.</p>}
          <pre>{JSON.stringify({ proposition, source_ids: sourceIds, research_notes: claimForm.research_notes || "" }, null, 2)}</pre>
        </div>
        <div className="prov-actions">
          <button className="prov-primary" disabled={submitting || !proposition || !propositionReady(proposition)}>
            {submitting ? "Submitting…" : "Create claim"}
          </button>
        </div>
      </form>
    </section>
  );
}
