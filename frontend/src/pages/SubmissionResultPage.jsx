import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

// US-07: a graded submission — the score and whether each answer was right. The correct
// answers are not shown: the API never sends them.
export default function SubmissionResultPage() {
  const { submissionId } = useParams()
  const { authFetch } = useAuth()
  const [submission, setSubmission] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch(`/submissions/${submissionId}/`)
      .then((data) => {
        if (!ignore) setSubmission(data)
      })
      .catch((err) => {
        // 404 for someone else's submission → "Илгээлт олдсонгүй."
        if (!ignore) setError(formErrors(err).general)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, submissionId])

  if (error) {
    return (
      <section>
        <p>
          <Link to="/student">← Миний ангиуд</Link>
        </p>
        <p className="alert" role="alert">
          {error}
        </p>
      </section>
    )
  }
  if (!submission) {
    return <p className="muted">Ачаалж байна…</p>
  }

  return (
    <section>
      <p>
        <Link to={`/student/classes/${submission.classroom}`}>← Анги руу буцах</Link>
      </p>
      <h1>{submission.assignment_title}</h1>
      <p className="score">
        Оноо:{' '}
        <strong>
          {submission.score} / {submission.max_score}
        </strong>{' '}
        ({submission.percent}%)
      </p>
      <p className="muted">Илгээсэн: {new Date(submission.submitted_at).toLocaleString('mn-MN')}</p>

      <h2>Асуулт бүрийн дүн</h2>
      <ol className="question-list">
        {submission.results.map((result) => (
          <li className="status" key={result.question}>
            <div className="list-row">
              <strong>{result.text}</strong>
              <span className={result.is_correct ? 'correct' : 'wrong'}>
                {result.is_correct ? '✓ Зөв' : '✗ Буруу'}
              </span>
            </div>
            <p className="muted">
              Таны хариулт: {result.your_answer ?? 'хариулаагүй'} · {result.points_awarded} /{' '}
              {result.points} оноо
            </p>
          </li>
        ))}
      </ol>
    </section>
  )
}
