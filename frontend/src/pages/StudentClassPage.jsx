import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

// What the student can do with an assignment (US-07): see their result, or solve it.
function AssignmentAction({ assignment }) {
  if (assignment.submission) {
    const { id, score, max_score: maxScore } = assignment.submission
    return (
      <Link to={`/student/submissions/${id}`}>
        Илгээсэн — {score}/{maxScore}
      </Link>
    )
  }
  if (assignment.is_open && assignment.question_count > 0) {
    return (
      <Link className="button" to={`/student/assignments/${assignment.id}`}>
        Ажиллах
      </Link>
    )
  }
  return null
}

// One class as a student sees it (US-03), opened after joining or from "Миний ангиуд".
// US-05: the class's assignments, with their due dates. US-07: solve them, see the results.
export default function StudentClassPage() {
  const { classId } = useParams()
  const { authFetch } = useAuth()
  const [classroom, setClassroom] = useState(null)
  const [error, setError] = useState(null)
  const [assignments, setAssignments] = useState([])
  const [loadingAssignments, setLoadingAssignments] = useState(true)
  const [assignmentsError, setAssignmentsError] = useState(null)

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

  useEffect(() => {
    let ignore = false
    authFetch(`/assignments/?classroom=${classId}`)
      .then((data) => {
        if (!ignore) setAssignments(data)
      })
      .catch((err) => {
        if (!ignore) setAssignmentsError(formErrors(err).general)
      })
      .finally(() => {
        if (!ignore) setLoadingAssignments(false)
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
      {assignmentsError ? (
        <p className="alert" role="alert">
          {assignmentsError}
        </p>
      ) : loadingAssignments ? (
        <p className="muted">Даалгавруудыг ачаалж байна…</p>
      ) : assignments.length === 0 ? (
        <p className="muted">Энэ ангид одоогоор даалгавар алга.</p>
      ) : (
        <ul className="status-list">
          {assignments.map((assignment) => (
            <li className="status" key={assignment.id}>
              <div className="list-row">
                <span>
                  <strong>{assignment.title}</strong> · {assignment.question_count} асуулт ·
                  Дуусах: {new Date(assignment.due_date).toLocaleString('mn-MN')}{' '}
                  <span className={assignment.is_open ? 'badge ok' : 'badge'}>
                    {assignment.is_open ? 'Нээлттэй' : 'Хугацаа дууссан'}
                  </span>
                </span>
                <AssignmentAction assignment={assignment} />
              </div>
              {assignment.instructions && <p className="muted">{assignment.instructions}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
