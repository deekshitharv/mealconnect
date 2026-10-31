// One label + field + error message. Use as="select" or as="textarea" for those.
export default function FormInput({ label, id, error, hint, as: Tag = "input", children, ...rest }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <Tag id={id} className={error ? "input has-error" : "input"} aria-invalid={Boolean(error)} {...rest}>
        {children}
      </Tag>
      {hint && !error && <small className="hint">{hint}</small>}
      {error && <small className="error-text">{error}</small>}
    </div>
  );
}