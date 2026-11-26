import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import QuestionForm from '../components/QuestionForm.jsx'

const KIND_LABELS = {
  multiple_choice: 'Олон сонголттой',
  fill_in: 'Нөхөх',
}

// US-06: the teacher's page for one assignment — its questions and the form to add more.
export default function AssignmentEditorPage() {
  const { assignmentId } = useParams()
  const { authFetch } = useAuth()
  const [assignment, setAssignment] = useState(null)
  const [questions, setQuestions] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch(`/assignments/${assignmentId}/`)
      .then((data) => {
        if (!ignore) {
          setAssignment(data)
          setQuestions(data.questions)
        }
      })
      .catch((err) => {
        // 404 for another teacher's assignment → "Даалгавар олдсонгүй."
        if (!ignore) setError(formErrors(err).general)
      })
    return () => {
      ignore = true
    }
  }, [authFetch, assignmentId])

  async function handleDelete(question) {
    if (!window.confirm('Энэ асуултыг устгах уу?')) {
      return
    }
    setError(null)
    try {
      await authFetch(`/assignments/${assignmentId}/questions/${question.id}/`, {
        method: 'DELETE',
      })
      setQuestions((current) => current.filter((item) => item.id !== question.id))
    } catch (err) {
      setError(formErrors(err).general)
    }
  }

  if (!assignment) {
    return error ? (
      <section>
        <p>
          <Link to="/teacher">← Багшийн самбар</Link>
        </p>
        <p className="alert" role="alert">
          {error}
        </p>
      </section>
    ) : (
      <p className="muted">Ачаалж байна…</p>
    )
  }

  return (
    <section>
      <p>
        <Link to={`/teacher/classes/${assignment.classroom}`}>← Анги руу буцах</Link>
      </p>
      <h1>{assignment.title}</h1>
      <p>
        Дуусах: {new Date(assignment.due_date).toLocaleString('mn-MN')}{' '}
        <span className={assignment.is_open ? 'badge ok' : 'badge'}>
          {assignment.is_open ? 'Нээлттэй' : 'Хугацаа дууссан'}
        </span>
      </p>
      {assignment.instructions && <p className="muted">{assignment.instructions}</p>}
      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}

      <h2>Асуултууд ({questions.length})</h2>
      {questions.length === 0 ? (
        <p className="muted">Одоогоор асуулт алга. Доорх формоор нэмнэ үү.</p>
      ) : (
        <ol className="question-list">
          {questions.map((question) => (
            <li className="status" key={question.id}>
              <div className="list-row">
                <span>
                  <span className="badge">{KIND_LABELS[question.kind]}</span>{' '}
                  <strong>{question.text}</strong> · {question.points} оноо
                </span>
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => handleDelete(question)}
                >
                  Устгах
                </button>
              </div>
              {question.kind === 'multiple_choice' ? (
                <ul>
                  {question.choices.map((choice) => (
                    <li key={choice.id} className={choice.is_correct ? 'correct' : undefined}>
                      {choice.text}
                      {choice.is_correct && ' ✓ зөв'}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  Зөв хариулт: <span className="correct">{question.correct_answer}</span>
                </p>
              )}
            </li>
          ))}
        </ol>
      )}

      <QuestionForm
        assignmentId={assignmentId}
        onCreated={(question) => setQuestions((current) => [...current, question])}
      />
    </section>
  )
}
