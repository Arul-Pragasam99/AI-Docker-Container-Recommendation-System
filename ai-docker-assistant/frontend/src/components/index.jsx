import "./components.css";

/* ── Button ──────────────────────────────────────────────────────────────── */
export function Button({ children, loading, disabled, onClick, variant = "primary" }) {
  return (
    <button
      className={`btn btn-${variant}${loading ? " btn-loading" : ""}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <span className="spinner" /> : null}
      {children}
    </button>
  );
}

/* ── Card ────────────────────────────────────────────────────────────────── */
export function Card({ children, className = "" }) {
  return <div className={`card ${className}`}>{children}</div>;
}

/* ── Section label ───────────────────────────────────────────────────────── */
export function Label({ children }) {
  return <span className="field-label">{children}</span>;
}

/* ── CodeBlock ───────────────────────────────────────────────────────────── */
export function CodeBlock({ code, language = "" }) {
  const copy = () => navigator.clipboard.writeText(code);
  return (
    <div className="code-block">
      <div className="code-block-header">
        <span className="code-lang muted">{language}</span>
        <button className="copy-btn" onClick={copy}>Copy</button>
      </div>
      <pre><code>{code}</code></pre>
    </div>
  );
}

/* ── Badge ───────────────────────────────────────────────────────────────── */
export function Badge({ children, color = "default" }) {
  return <span className={`badge badge-${color}`}>{children}</span>;
}

/* ── SeverityBadge ───────────────────────────────────────────────────────── */
export function SeverityBadge({ severity }) {
  const map = { low: "green", medium: "yellow", high: "orange", critical: "red" };
  return <Badge color={map[severity] || "default"}>{severity}</Badge>;
}

/* ── ConfidenceBar ───────────────────────────────────────────────────────── */
export function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? "var(--green)" : pct >= 55 ? "var(--yellow)" : "var(--orange)";
  return (
    <div className="confidence-wrap">
      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="confidence-label" style={{ color }}>{pct}%</span>
    </div>
  );
}

/* ── ErrorBox ────────────────────────────────────────────────────────────── */
export function ErrorBox({ message }) {
  if (!message) return null;
  return <div className="error-box">⚠ {message}</div>;
}

/* ── Select ──────────────────────────────────────────────────────────────── */
export function Select({ value, onChange, options }) {
  return (
    <select className="field-input" value={value} onChange={e => onChange(e.target.value)}>
      {options.map(o => (
        <option key={o.value ?? o} value={o.value ?? o}>
          {o.label ?? o}
        </option>
      ))}
    </select>
  );
}

/* ── NumberInput ─────────────────────────────────────────────────────────── */
export function NumberInput({ value, onChange, min, max, placeholder }) {
  return (
    <input
      className="field-input"
      type="number"
      value={value}
      min={min}
      max={max}
      placeholder={placeholder}
      onChange={e => onChange(+e.target.value)}
    />
  );
}

/* ── Toggle ──────────────────────────────────────────────────────────────── */
export function Toggle({ checked, onChange, label }) {
  return (
    <label className="toggle-wrap">
      <div className={`toggle${checked ? " on" : ""}`} onClick={() => onChange(!checked)}>
        <div className="toggle-thumb" />
      </div>
      <span>{label}</span>
    </label>
  );
}
