import { useState } from 'react'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'
import FormField from './FormField.jsx'

const MIN_CHOICES = 2
const MAX_CHOICES = 6

// Each choice row needs a stable key while rows are added and removed.
let nextChoiceId = 1
function newChoice() {
  return { id: nextChoiceId++, text: '' }
}
function startingChoices() {
  return Array.from({ length: MIN_CHOICES }, newChoice)
}

// US-06: add a question to an assignment from one of two templates — multiple choice
// (2–6 options, exactly one correct) or fill-in (one correct answer).
//
//   <QuestionForm assignmentId={id} onCreated={(question) => ...} />
export default function QuestionForm({ assignmentId, onCreated }) {
  const { authFetch } = useAuth()
  const [kind, setKind] = useState('multiple_choice')
  const [text, setText] = useState('')
  const [points, setPoints] = useState('1')
  const [choices, setChoices] = useState(startingChoices)
  const [correctId, setCorrectId] = useState(null)
  const [correctAnswer, setCorrectAnswer] = useState('')
  const [errors, setErrors] = useState({ fields: {} })
  const [submitting, setSubmitting] = useState(false)
  const [saved, setSaved] = useState(false)

  function changeChoice(id, value) {
    setChoices((current) => current.map((c) => (c.id === id ? { ...c, text: value } : c)))
  }

  function removeChoice(id) {
    setChoices((current) => current.filter((c) => c.id !== id))
    if (correctId === id) setCorrectId(null)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaved(false)
    // Same rule as the backend; checked here so the teacher gets the message at once.
    if (kind === 'multiple_choice' && correctId === null) {
      setErrors({ fields: { choices: 'Зөв хариултыг сонгоно уу.' } })
      return
    }
    const body =
      kind === 'multiple_choice'
        ? {
            kind,
            text,
            points: Number(points),
            choices: choices.map((c) => ({ text: c.text, is_correct: c.id === correctId })),
          }
        : { kind, text, points: Number(points), correct_answer: correctAnswer }

    setSubmitting(true)
    setErrors({ fields: {} })
    try {
      const question = await authFetch(`/assignments/${assignmentId}/questions/`, {
        method: 'POST',
        body,
      })
      onCreated(question)
      setText('')
      setPoints('1')
      setChoices(startingChoices())
      setCorrectId(null)
      setCorrectAnswer('')
      setSaved(true)
    } catch (error) {
      setErrors(formErrors(error))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Асуулт нэмэх</h2>
      {errors.general && (
        <p className="alert" role="alert">
          {errors.general}
        </p>
      )}
      {saved && (
        <p className="status ok" role="status">
          Асуулт хадгалагдлаа.
        </p>
      )}

      <fieldset className="field">
        <legend className="field-label">Загвар</legend>
        <div className="radio-options">
          <label className="radio">
            <input
              type="radio"
              name="kind"
              value="multiple_choice"
              checked={kind === 'multiple_choice'}
              onChange={() => setKind('multiple_choice')}
            />
            Олон сонголттой
          </label>
          <label className="radio">
            <input
              type="radio"
              name="kind"
              value="fill_in"
              checked={kind === 'fill_in'}
              onChange={() => setKind('fill_in')}
            />
            Нөхөх
          </label>
        </div>
        {errors.fields.kind && <span className="field-error">{errors.fields.kind}</span>}
      </fieldset>

      <FormField label="Асуулт" error={errors.fields.text}>
        <textarea
          name="text"
          rows={3}
          required
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
      </FormField>

      <FormField label="Оноо" error={errors.fields.points}>
        <input
          type="number"
          name="points"
          className="points-input"
          min={1}
          max={100}
          required
          value={points}
          onChange={(event) => setPoints(event.target.value)}
        />
      </FormField>

      {kind === 'multiple_choice' ? (
        <fieldset className="field">
          <legend className="field-label">Сонголтууд</legend>
          <span className="field-hint">Зөв хариултын хажууд "Зөв"-ийг сонгоно.</span>
          {choices.map((choice, index) => (
            <div className="choice-row" key={choice.id}>
              <input
                type="text"
                aria-label={`Сонголт ${index + 1}`}
                maxLength={255}
                value={choice.text}
                onChange={(event) => changeChoice(choice.id, event.target.value)}
              />
              <label className="radio">
                <input
                  type="radio"
                  name="correct"
                  checked={correctId === choice.id}
                  onChange={() => setCorrectId(choice.id)}
                />
                Зөв
              </label>
              {choices.length > MIN_CHOICES && (
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => removeChoice(choice.id)}
                >
                  Хасах
                </button>
              )}
            </div>
          ))}
          {choices.length < MAX_CHOICES && (
            <p>
              <button
                type="button"
                className="button secondary"
                onClick={() => setChoices((current) => [...current, newChoice()])}
              >
                Сонголт нэмэх
              </button>
            </p>
          )}
          {errors.fields.choices && <span className="field-error">{errors.fields.choices}</span>}
        </fieldset>
      ) : (
        <FormField label="Зөв хариулт" error={errors.fields.correct_answer}>
          <input
            type="text"
            name="correct_answer"
            maxLength={255}
            required
            value={correctAnswer}
            onChange={(event) => setCorrectAnswer(event.target.value)}
          />
        </FormField>
      )}

      <p>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Хадгалж байна…' : 'Асуулт хадгалах'}
        </button>
      </p>
    </form>
  )
}
