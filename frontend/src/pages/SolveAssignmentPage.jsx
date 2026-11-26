import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

// US-07: a student answers an assignment one question at a time and submits it. The answers
// are graded at once and the result page opens. Already submitted → straight to the result.
export default function SolveAssignmentPage() {
  const { assignmentId } = useParams()
  const { authFetch } = useAuth()
  const navigate = useNavigate()
  const [assignment, setAssignment] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [index, setIndex] = useState(0)
  // question id → { choice: option id } (multiple choice) or { text } (fill-in)
  const [answers, setAnswers] = useState({})
  const [submitError, setSubmitError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let ignore = false
    authFetch(`/assignments/${assignmentId}/`)
      .then((data) => {
        if (!ignore) setAssignment(data)
      })
      .catch((err) => {
        // 404 for an assignment of a class the student has not joined → "Даалгавар олдсонгүй."
        if (!ignore) setLoadError(formErrors(err).general)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, assignmentId])

  if (loadError) {
    return (
      <section>
        <p>
          <Link to="/student">← Миний ангиуд</Link>
        </p>
        <p className="alert" role="alert">
          {loadError}
        </p>
      </section>
    )
  }
  if (!assignment) {
    return <p className="muted">Ачаалж байна…</p>
  }
  if (assignment.submission) {
    return <Navigate to={`/student/submissions/${assignment.submission.id}`} replace />
  }

  const questions = assignment.questions
  const header = (
    <>
      <p>
        <Link to={`/student/classes/${assignment.classroom}`}>← Анги руу буцах</Link>
      </p>
      <h1>{assignment.title}</h1>
      <p className="muted">
        Дуусах: {new Date(assignment.due_date).toLocaleString('mn-MN')} · {questions.length} асуулт
      </p>
      {assignment.instructions && <p>{assignment.instructions}</p>}
    </>
  )

  if (!assignment.is_open) {
    return (
      <section>
        {header}
        <p className="alert">Даалгаврын хугацаа дууссан байна.</p>
      </section>
    )
  }
  if (questions.length === 0) {
    return (
      <section>
        {header}
        <p className="muted">Энэ даалгаварт асуулт алга байна.</p>
      </section>
    )
  }

  function isAnswered(question) {
    const answer = answers[question.id]
    return question.kind === 'multiple_choice'
      ? answer?.choice !== undefined
      : Boolean(answer?.text?.trim())
  }

  function setAnswer(questionId, answer) {
    setAnswers((current) => ({ ...current, [questionId]: answer }))
  }

  async function handleSubmit() {
    const unanswered = questions.filter((q) => !isAnswered(q)).length
    if (unanswered > 0 && !window.confirm(`${unanswered} асуулт хариулаагүй байна. Илгээх үү?`)) {
      return
    }
    setSubmitting(true)
    setSubmitError(null)
    try {
      const submission = await authFetch('/submissions/', {
        method: 'POST',
        body: {
          assignment: assignment.id,
          // Unanswered questions are left out; the backend grades them as wrong.
          answers: questions.filter(isAnswered).map((q) =>
            q.kind === 'multiple_choice'
              ? { question: q.id, choice: answers[q.id].choice }
              : { question: q.id, text: answers[q.id].text },
          ),
        },
      })
      navigate(`/student/submissions/${submission.id}`, { replace: true })
    } catch (error) {
      // e.g. "Даалгаврын хугацаа дууссан байна." or "Та энэ даалгаврыг аль хэдийн илгээсэн байна."
      const { general, fields } = formErrors(error)
      setSubmitError(general ?? Object.values(fields).join(' '))
      setSubmitting(false)
    }
  }

  const question = questions[index]
  const isLast = index === questions.length - 1
  const answeredCount = questions.filter(isAnswered).length

  return (
    <section>
      {header}
      {submitError && (
        <p className="alert" role="alert">
          {submitError}
        </p>
      )}

      <fieldset className="field question-card">
        <legend className="field-label">
          Асуулт {index + 1} / {questions.length} · {question.points} оноо
        </legend>
        <p className="question-text">{question.text}</p>
        {question.kind === 'multiple_choice' ? (
          <div className="choice-list">
            {question.choices.map((choice) => (
              <label className="radio" key={choice.id}>
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  checked={answers[question.id]?.choice === choice.id}
                  onChange={() => setAnswer(question.id, { choice: choice.id })}
                />
                {choice.text}
              </label>
            ))}
          </div>
        ) : (
          <input
            type="text"
            aria-label="Хариулт"
            maxLength={255}
            autoComplete="off"
            value={answers[question.id]?.text ?? ''}
            onChange={(event) => setAnswer(question.id, { text: event.target.value })}
          />
        )}
      </fieldset>

      <div className="actions">
        {index > 0 && (
          <button type="button" className="button secondary" onClick={() => setIndex(index - 1)}>
            Өмнөх
          </button>
        )}
        {isLast ? (
          <button type="button" className="button" disabled={submitting} onClick={handleSubmit}>
            {submitting ? 'Илгээж байна…' : 'Илгээх'}
          </button>
        ) : (
          <button type="button" className="button" onClick={() => setIndex(index + 1)}>
            Дараах
          </button>
        )}
      </div>
      <p className="muted">
        {answeredCount} / {questions.length} асуултад хариулсан
      </p>
    </section>
  )
}
