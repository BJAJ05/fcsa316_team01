import { useState } from 'react'
import { Link, Navigate } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import { dashboardPath, ROLE_LABELS } from '../auth/roles.js'
import FormField from '../components/FormField.jsx'

// US-01: sign up as a teacher or a student. On success the user is logged in and
// lands on the dashboard for the chosen role.
export default function RegisterPage() {
  const { user, register } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to={dashboardPath(user.role)} replace />
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({ fields: {} })
    try {
      await register(email, password, role)
    } catch (error) {
      setErrors(formErrors(error))
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-card">
      <h1>Бүртгүүлэх</h1>
      <form className="form" onSubmit={handleSubmit}>
        {errors.general && (
          <p className="alert" role="alert">
            {errors.general}
          </p>
        )}
        <FormField label="Имэйл" error={errors.fields.email}>
          <input
            type="email"
            name="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </FormField>
        <FormField
          label="Нууц үг"
          hint="Хамгийн багадаа 8 тэмдэгт, зөвхөн тоо биш."
          error={errors.fields.password}
        >
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </FormField>
        <fieldset className="field">
          <legend className="field-label">Дүр</legend>
          <div className="radio-options">
            {Object.entries(ROLE_LABELS).map(([value, label]) => (
              <label key={value} className="radio">
                <input
                  type="radio"
                  name="role"
                  value={value}
                  required
                  checked={role === value}
                  onChange={() => setRole(value)}
                />
                {label}
              </label>
            ))}
          </div>
          {errors.fields.role && <span className="field-error">{errors.fields.role}</span>}
        </fieldset>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Бүртгэж байна…' : 'Бүртгүүлэх'}
        </button>
      </form>
      <p className="muted">
        Бүртгэлтэй юу? <Link to="/login">Нэвтрэх</Link>
      </p>
    </section>
  )
}
