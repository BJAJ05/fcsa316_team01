import { useEffect, useState } from 'react'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import FormField from '../components/FormField.jsx'

// Teacher's start page after login (US-01). US-02 lets teachers create and share classes.
export default function TeacherDashboardPage() {
  const { user, authFetch } = useAuth()
  const [classes, setClasses] = useState([])
  const [name, setName] = useState('')
  const [subject, setSubject] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [createdCode, setCreatedCode] = useState(null)
  const [loadingClasses, setLoadingClasses] = useState(true)
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

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({ fields: {} })
    setCreatedCode(null)
    try {
      const classroom = await authFetch('/classes/', {
        method: 'POST',
        body: { name, subject },
      })
      setClasses((current) => [classroom, ...current])
      setName('')
      setSubject('')
      setCreatedCode(classroom.code)
    } catch (error) {
      setErrors(formErrors(error))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section>
      <h1>Багшийн самбар</h1>
      <p>Сайн байна уу, {user.email}!</p>
      <h2>Шинэ анги үүсгэх</h2>
      <form className="form" onSubmit={handleSubmit}>
        {errors.general && (
          <p className="alert" role="alert">
            {errors.general}
          </p>
        )}
        {createdCode && (
          <p className="status ok" role="status">
            Анги үүслээ. Сурагчдадаа нэгдэх кодыг хуваалцаарай: <strong>{createdCode}</strong>
          </p>
        )}
        <FormField label="Ангийн нэр" error={errors.fields.name}>
          <input
            type="text"
            name="name"
            maxLength={100}
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </FormField>
        <FormField label="Хичээлийн нэр" error={errors.fields.subject}>
          <input
            type="text"
            name="subject"
            maxLength={100}
            required
            value={subject}
            onChange={(event) => setSubject(event.target.value)}
          />
        </FormField>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Үүсгэж байна…' : 'Анги үүсгэх'}
        </button>
      </form>

      <h2>Таны ангиуд</h2>
      {loadingClasses ? (
        <p className="muted">Ангиудыг ачаалж байна…</p>
      ) : classes.length === 0 ? (
        <p className="muted">Одоогоор үүсгэсэн анги алга.</p>
      ) : (
        <ul className="status-list">
          {classes.map((classroom) => (
            <li className="status" key={classroom.id}>
              <strong>{classroom.name}</strong> · {classroom.subject} — Нэгдэх код:{' '}
              <strong>{classroom.code}</strong> · {classroom.student_count} сурагч
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
