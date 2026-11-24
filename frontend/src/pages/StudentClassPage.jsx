import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

// One class as a student sees it (US-03), opened after joining or from "Миний ангиуд".
// The class's assignments (US-05, US-07) will be listed here.
export default function StudentClassPage() {
  const { classId } = useParams()
  const { authFetch } = useAuth()
  const [classroom, setClassroom] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch(`/classes/${classId}/`)
      .then((data) => {
        if (!ignore) setClassroom(data)
      })
      .catch((err) => {
        // 404 for a class the student has not joined → "Анги олдсонгүй."
        if (!ignore) setError(formErrors(err).general)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, classId])

  const backLink = (
    <p>
      <Link to="/student">← Миний ангиуд</Link>
    </p>
  )

  if (error) {
    return (
      <section>
        {backLink}
        <p className="alert" role="alert">
          {error}
        </p>
      </section>
    )
  }
  if (!classroom) {
    return <p className="muted">Ачаалж байна…</p>
  }

  return (
    <section>
      {backLink}
      <h1>{classroom.name}</h1>
      <p>
        {classroom.subject} · Багш: {classroom.teacher_email} · {classroom.student_count} сурагч
      </p>

      <h2>Даалгаврууд</h2>
      <p className="muted">Энэ ангид одоогоор даалгавар алга.</p>
    </section>
  )
}
