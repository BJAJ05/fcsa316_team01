import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import FormField from './FormField.jsx'

// Earliest due date first, the same order as the backend.
function byDueDate(a, b) {
  return new Date(a.due_date) - new Date(b.due_date)
}

// US-05: a teacher's assignments in one class, with a "new assignment" form.
// US-06: each assignment links to its editor page, where questions are added.
// Used on the teacher's class page:  <AssignmentSection classId={classId} />
export default function AssignmentSection({ classId }) {
  const { authFetch } = useAuth()
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [listError, setListError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [instructions, setInstructions] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch(`/assignments/?classroom=${classId}`)
      .then((data) => {
        if (!ignore) setAssignments(data)
      })
      .catch((error) => {
        if (!ignore) setListError(formErrors(error).general)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, classId])

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({ fields: {} })
    setCreated(null)
    try {
      const assignment = await authFetch('/assignments/', {
        method: 'POST',
        body: {
          classroom: Number(classId),
          title,
          instructions,
          // <input type="datetime-local"> gives local time without a zone; send it as UTC.
          due_date: dueDate ? new Date(dueDate).toISOString() : null,
        },
      })
      setAssignments((current) => [...current, assignment].sort(byDueDate))
      setTitle('')
      setInstructions('')
      setDueDate('')
      setShowForm(false)
      setCreated(assignment.title)
    } catch (error) {
      setErrors(formErrors(error))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(assignment) {
    if (!window.confirm(`"${assignment.title}" даалгаврыг устгах уу?`)) {
      return
    }
    setListError(null)
    try {
      await authFetch(`/assignments/${assignment.id}/`, { method: 'DELETE' })
      setAssignments((current) => current.filter((item) => item.id !== assignment.id))
    } catch (error) {
      setListError(formErrors(error).general)
    }
  }

  return (
    <section>
      <h2>Даалгаврууд</h2>
      {listError && (
        <p className="alert" role="alert">
          {listError}
        </p>
      )}
      {created && (
        <p className="status ok" role="status">
          "{created}" даалгавар үүслээ. Ангийн сурагчдад харагдана.
        </p>
      )}

      {loading ? (
        <p className="muted">Даалгавруудыг ачаалж байна…</p>
      ) : assignments.length === 0 ? (
        <p className="muted">Энэ ангид одоогоор даалгавар алга.</p>
      ) : (
        <ul className="status-list">
          {assignments.map((assignment) => (
            <li className="status list-row" key={assignment.id}>
              <span>
                <Link to={`/teacher/assignments/${assignment.id}`}>
                  <strong>{assignment.title}</strong>
                </Link>{' '}
                · {assignment.question_count} асуулт · Дуусах:{' '}
                {new Date(assignment.due_date).toLocaleString('mn-MN')}{' '}
                <span className={assignment.is_open ? 'badge ok' : 'badge'}>
                  {assignment.is_open ? 'Нээлттэй' : 'Хугацаа дууссан'}
                </span>
              </span>
              <button
                type="button"
                className="button secondary"
                onClick={() => handleDelete(assignment)}
              >
                Устгах
              </button>
            </li>
          ))}
        </ul>
      )}

      {showForm ? (
        <form className="form" onSubmit={handleSubmit}>
          <h3>Шинэ даалгавар</h3>
          {errors.general && (
            <p className="alert" role="alert">
              {errors.general}
            </p>
          )}
          <FormField label="Даалгаврын нэр" error={errors.fields.title}>
            <input
              type="text"
              name="title"
              maxLength={200}
              required
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </FormField>
          <FormField label="Заавар" hint="Заавал биш" error={errors.fields.instructions}>
            <textarea
              name="instructions"
              rows={4}
              value={instructions}
              onChange={(event) => setInstructions(event.target.value)}
            />
          </FormField>
          <FormField label="Дуусах хугацаа" error={errors.fields.due_date}>
            <input
              type="datetime-local"
              name="due_date"
              required
              value={dueDate}
              onChange={(event) => setDueDate(event.target.value)}
            />
          </FormField>
          <div className="actions">
            <button type="submit" className="button" disabled={submitting}>
              {submitting ? 'Хадгалж байна…' : 'Хадгалах'}
            </button>
            <button type="button" className="button secondary" onClick={() => setShowForm(false)}>
              Болих
            </button>
          </div>
        </form>
      ) : (
        <p>
          <button
            type="button"
            className="button"
            onClick={() => {
              setShowForm(true)
              setCreated(null)
            }}
          >
            Шинэ даалгавар
          </button>
        </p>
      )}
    </section>
  )
}
