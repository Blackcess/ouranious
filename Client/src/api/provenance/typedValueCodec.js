// The API preserves ordinary JSON. Its tagged codec supports only the fixed
// registry in Knowledge Base/application/persistence/typed_value_codec.py.
const TAGS = new Set(["decimal", "datetime", "date", "uuid", "enum", "dict", "tuple", "set", "frozenset", "dataclass"]);
const ENUMS = new Set(["identity_kind", "lifecycle_state", "place_kind", "organisation_classification", "investment_stage", "investment_types", "startup_stage", "startup_business_model", "claim_status", "source_type", "assessment_outcome", "relationship_type", "acquisition_type", "founding_stage", "headquarters_function", "headquarters_level", "operating_status", "ownership_type", "partnership_status", "availability_status", "development_status", "offering_status", "duration_unit"]);
const DATACLASSES = new Set(["identity_reference", "relationship_reference", "source_reference", "identity_representations", "source", "verification_assessment", "identity_attribute_proposition", "relationship_proposition", "relationship_property_proposition", "identity_proposal_proposition", "money", "duration", "investment_terms", "acquisition_properties", "founder_properties", "headquarters_properties", "industry_participation_properties", "investment_properties", "leadership_properties", "market_presence_properties", "ownership_properties", "partnership_properties", "product_availability_properties", "product_development_properties", "product_offering_properties", "product_technology_properties", "residence_properties", "technology_adoption_properties"]);

export function validateTypedValue(value, path = "value") {
  if (Array.isArray(value)) { value.forEach((item, index) => validateTypedValue(item, `${path}[${index}]`)); return; }
  if (!value || typeof value !== "object") return;
  if (!("$type" in value)) { Object.entries(value).forEach(([key, item]) => validateTypedValue(item, `${path}.${key}`)); return; }
  const tag = value.$type;
  if (!TAGS.has(tag)) throw new Error(`${path}: unsupported typed-value tag “${tag}”.`);
  if (tag === "enum" && !ENUMS.has(value.class)) throw new Error(`${path}: unsupported enum class “${value.class}”.`);
  if (tag === "dataclass" && !DATACLASSES.has(value.class)) throw new Error(`${path}: unsupported dataclass class “${value.class}”.`);
  if (["dict", "tuple", "set", "frozenset"].includes(tag) && !Array.isArray(tag === "dict" ? value.items : value.items)) throw new Error(`${path}: malformed ${tag} value.`);
  if (["decimal", "datetime", "date", "uuid"].includes(tag) && typeof value.value !== "string") throw new Error(`${path}: malformed ${tag} value.`);
}

export function parseJsonValue(text, label = "Value") {
  let value;
  try { value = JSON.parse(text); } catch { throw new Error(`${label} must be valid JSON.`); }
  validateTypedValue(value, label);
  return value;
}

export function decodeTypedValue(value) {
  if (Array.isArray(value)) return value.map(decodeTypedValue);
  if (!value || typeof value !== "object") return value;
  if (!Object.prototype.hasOwnProperty.call(value, "$type")) return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, decodeTypedValue(item)]));
  const items = (entries) => entries.map((entry) => decodeTypedValue(entry));
  switch (value.$type) {
    case "decimal": case "datetime": case "date": case "uuid": case "enum": return value.value;
    case "tuple": case "set": case "frozenset": return items(value.items);
    case "dict": {
      const decoded = value.items.map(([key, item]) => [decodeTypedValue(key), decodeTypedValue(item)]);
      if (decoded.every(([key]) => typeof key === "string")) return Object.fromEntries(decoded);
      return { typedKind: "dict", entries: decoded };
    }
    case "dataclass": return { typedKind: "dataclass", class: value.class, fields: decodeTypedValue(value.fields) };
    default: throw new Error(`Unsupported typed-value tag “${value.$type}”.`);
  }
}

export function decodeClaimValues(claim) {
  if (!claim?.proposition) return claim;
  const p = { ...claim.proposition };
  if (p.proposition_type === "identity_attribute" || p.proposition_type === "relationship_property") p.proposed_value = decodeTypedValue(p.proposed_value);
  if (p.proposition_type === "identity_proposal") p.attributes = decodeTypedValue(p.attributes);
  return { ...claim, proposition: p };
}
