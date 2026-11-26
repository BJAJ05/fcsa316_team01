import { useEffect, useState } from 'react'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

// US-04: the students of one class, and removing a student from it.
// Used on the teacher's class page:  <ClassRoster classId={classId} />
export default function ClassRoster({ classId }) {
  const { authFetch } = useAuth()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch(`/classes/${classId}/students/`)
      .then((data) => {
        if (!ignore) setStudents(data)
      })
      .catch((err) => {
        if (!ignore) setError(formErrors(err).general)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, classId])

  async function handleRemove(student) {
    if (!window.confirm(`${student.email} сурагчийг ангиас хасах уу?`)) {
      return
    }
    setError(null)
    try {
      await authFetch(`/classes/${classId}/students/${student.id}/`, { method: 'DELETE' })
      setStudents((current) => current.filter((item) => item.id !== student.id))
    } catch (err) {
      setError(formErrors(err).general)
    }
  }

  return (
    <section>
      <h2>Сурагчдын жагсаалт ({students.length})</h2>
      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}
      {loading ? (
        <p className="muted">Сурагчдыг ачаалж байна…</p>
      ) : students.length === 0 ? (
        <p className="muted">Одоогоор элссэн сурагч алга. Ангийн кодоо сурагчдадаа хуваалцаарай.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Имэйл</th>
              <th>Элссэн</th>
              <th>
                <span className="visually-hidden">Үйлдэл</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.email}</td>
                <td>{new Date(student.joined_at).toLocaleString('mn-MN')}</td>
                <td className="table-actions">
                  <button
                    type="button"
                    className="button secondary"
                    onClick={() => handleRemove(student)}
                  >
                    Хасах
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
