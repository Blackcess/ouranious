import { useState } from "react";

export const label = (value = "") => value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());

export function Field({ title, children }) {
  return (
    <label className="prov-field">
      <span>{title}</span>
      {children}
    </label>
  );
}

export function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={onChange}>
      {options.map((option) => (
        <option key={option} value={option}>{label(option)}</option>
      ))}
    </select>
  );
}

export function IdBadge({ value }) {
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

export function Status({ value }) {
  return <span className={`prov-status status-${value}`}>{label(value)}</span>;
}
