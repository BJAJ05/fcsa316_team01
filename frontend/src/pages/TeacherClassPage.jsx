import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import AssignmentSection from '../components/AssignmentSection.jsx'
import ClassCode from '../components/ClassCode.jsx'
import ClassRoster from '../components/ClassRoster.jsx'

// One class as its teacher sees it (US-04): the code to share, the students and the
// assignments. Each section is its own component, so a story adds it here with one line
// (US-05: AssignmentSection; US-13 will add the "Дүн ба тайлан" link).
export default function TeacherClassPage() {
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
        // 404 for another teacher's class → "Анги олдсонгүй."
        if (!ignore) setError(formErrors(err).general)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, classId])

  const backLink = (
    <p>
      <Link to="/teacher">← Багшийн самбар</Link>
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
        {classroom.subject} · Нэгдэх код: <ClassCode code={classroom.code} />
      </p>

      <ClassRoster classId={classId} />
      <AssignmentSection classId={classId} />
    </section>
  )
}
