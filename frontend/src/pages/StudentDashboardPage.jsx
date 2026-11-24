import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import FormField from '../components/FormField.jsx'

const CODE_LENGTH = 6

// Student's start page after login (US-01). US-03: join a class with its code and see the
// joined classes. Exercises (US-07) and progress (US-12) come later.
export default function StudentDashboardPage() {
  const { user, authFetch } = useAuth()
  const navigate = useNavigate()
  const [classes, setClasses] = useState([])
  const [loadingClasses, setLoadingClasses] = useState(true)
  const [code, setCode] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let ignore = false
    authFetch('/classes/')
      .then((data) => {
        if (!ignore) setClasses(data)
      })
      .catch((error) => {
        if (!ignore) setErrors(formErrors(error))
      })
      .finally(() => {
        if (!ignore) setLoadingClasses(false)
      })
    return () => {
      ignore = true
    }
  }, [authFetch])

  // Codes are uppercase letters and digits: drop spaces and uppercase while typing/pasting.
  function handleCodeChange(event) {
    setCode(event.target.value.replace(/\s+/g, '').toUpperCase().slice(0, CODE_LENGTH))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({ fields: {} })
    try {
      const classroom = await authFetch('/classes/join/', { method: 'POST', body: { code } })
      navigate(`/student/classes/${classroom.id}`)
    } catch (error) {
      // e.g. 404 → "Ангийн код олдсонгүй."; already joined → message under the field.
      setErrors(formErrors(error))
      setSubmitting(false)
    }
  }

  return (
    <section>
      <h1>Сурагчийн самбар</h1>
      <p>Сайн байна уу, {user.email}!</p>

      <h2>Ангид элсэх</h2>
      <form className="form join-form" onSubmit={handleSubmit}>
        {errors.general && (
          <p className="alert" role="alert">
            {errors.general}
          </p>
        )}
        <FormField
          label="Ангийн код"
          hint="Багшаас авсан 6 тэмдэгттэй код, жишээ нь AB12CD"
          error={errors.fields.code}
        >
          <input
            type="text"
            name="code"
            className="code-input"
            autoComplete="off"
            spellCheck={false}
            required
            value={code}
            onChange={handleCodeChange}
          />
        </FormField>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Элсэж байна…' : 'Нэгдэх'}
        </button>
      </form>

      <h2>Миний ангиуд</h2>
      {loadingClasses ? (
        <p className="muted">Ангиудыг ачаалж байна…</p>
      ) : classes.length === 0 ? (
        <p className="muted">Та одоогоор ямар ч ангид элсээгүй байна.</p>
      ) : (
        <ul className="card-list">
          {classes.map((classroom) => (
            <li key={classroom.id}>
              <Link className="card" to={`/student/classes/${classroom.id}`}>
                <strong className="card-title">{classroom.name}</strong>
                <span>{classroom.subject}</span>
                <span className="muted">Багш: {classroom.teacher_email}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
