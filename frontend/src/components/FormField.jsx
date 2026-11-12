// One labelled form input with an optional hint and error message under it.
//
//   <FormField label="Имэйл" error={errors.fields.email}>
//     <input type="email" value={email} onChange={...} />
//   </FormField>
export default function FormField({ label, hint, error, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && !error && <span className="field-hint">{hint}</span>}
      {error && <span className="field-error">{error}</span>}
    </label>
  )
}
