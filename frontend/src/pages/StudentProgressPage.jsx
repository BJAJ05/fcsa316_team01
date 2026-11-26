import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formErrors } from '../api/formErrors.js'
import { useAuth } from '../auth/AuthContext.js'

export default function StudentProgressPage() {
  const { authFetch } = useAuth()
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    authFetch('/analytics/progress/')
      .then((data) => {
        if (!ignore) setClasses(data)
      })
      .catch((requestError) => {
        if (!ignore) setError(formErrors(requestError).general)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [authFetch])

  return (
    <section>
      <h1>Миний ахиц</h1>
      {error ? (
        <p className="alert" role="alert">
          {error}
        </p>
      ) : loading ? (
        <p className="muted">Ахицын мэдээллийг ачаалж байна…</p>
      ) : classes.length === 0 ? (
        <p className="muted">Та одоогоор ямар ч ангид элсээгүй байна.</p>
      ) : (
        <ul className="card-list progress-list">
          {classes.map((classroom) => (
            <li className="card progress-card" key={classroom.class_id}>
              <strong className="card-title">{classroom.class_name}</strong>
              <span>{classroom.subject}</span>
              <label className="progress-label">
                Гүйцэтгэл {classroom.completion_percent}%
                <progress value={classroom.completion_percent} max={100}>
                  {classroom.completion_percent}%
                </progress>
              </label>
              <p>
                Дундаж оноо:{' '}
                {classroom.average_percent === null ? '—' : `${classroom.average_percent}%`}
              </p>
              {classroom.assignments.length > 0 ? (
                <>
                  <h2>Даалгаврын оноо</h2>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart
                      data={classroom.assignments.map((assignment) => ({
                        ...assignment,
                        chartPercent: assignment.percent ?? 0,
                      }))}
                      margin={{ top: 8, right: 8, left: -20, bottom: 40 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="title"
                        angle={-25}
                        textAnchor="end"
                        interval={0}
                        height={56}
                      />
                      <YAxis domain={[0, 100]} />
                      <Tooltip
                        formatter={(value, _name, item) => [
                          item.payload.percent === null ? 'Илгээгээгүй' : `${value}%`,
                          'Оноо',
                        ]}
                      />
                      <Bar dataKey="chartPercent" fill="var(--accent)" />
                    </BarChart>
                  </ResponsiveContainer>
                  <ul className="progress-assignment-list">
                    {classroom.assignments.map((assignment) => (
                      <li key={assignment.id}>
                        {assignment.title}:{' '}
                        {assignment.percent === null ? 'Илгээгээгүй' : `${assignment.percent}%`}
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="muted">Энэ ангид одоогоор даалгавар алга.</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
