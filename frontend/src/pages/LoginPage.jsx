import { useState } from 'react'
import { Link, Navigate, useLocation } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import { dashboardPath } from '../auth/roles.js'
import FormField from '../components/FormField.jsx'

// US-01: log in with email and password, then open the dashboard for the user's role.
export default function LoginPage() {
  const { user, login } = useAuth()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [submitting, setSubmitting] = useState(false)

  // Already logged in (also right after a successful login): go to the page the user
  // wanted to open, or to their dashboard.
  if (user) {
    return <Navigate to={location.state?.from ?? dashboardPath(user.role)} replace />
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({ fields: {} })
    try {
      await login(email, password)
    } catch (error) {
      setErrors(formErrors(error))
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-card">
      <h1>Нэвтрэх</h1>
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
        <FormField label="Нууц үг" error={errors.fields.password}>
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </FormField>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Нэвтэрч байна…' : 'Нэвтрэх'}
        </button>
      </form>
      <p className="muted">
        Бүртгэлгүй юу? <Link to="/register">Бүртгүүлэх</Link>
      </p>
    </section>
  )
}
