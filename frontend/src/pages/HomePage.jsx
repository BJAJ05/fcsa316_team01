import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router'
import { ApiError, apiFetch } from '../api/client.js'
import { useAuth } from '../auth/AuthContext.js'
import { dashboardPath } from '../auth/roles.js'

// Start page for logged-out visitors: sign up / log in buttons, plus the development
// environment status (Frontend, Backend, database). Logged-in users go to their dashboard.
export default function HomePage() {
  const { user } = useAuth()

  if (user) {
    return <Navigate to={dashboardPath(user.role)} replace />
  }

  return (
    <section>
      <h1>Цахим сургалтын нэгдсэн платформ</h1>
      <p>
        Багш анги үүсгэж дасгал оруулдаг, сурагч ангийн кодоор нэгдэж дасгал ажиллан дүнгээ шууд
        хардаг цахим сургалтын платформ.
      </p>
      <div className="actions">
        <Link to="/register" className="button">
          Бүртгүүлэх
        </Link>
        <Link to="/login" className="button secondary">
          Нэвтрэх
        </Link>
      </div>
      <HealthStatus />
    </section>
  )
}

function HealthStatus() {
  const [health, setHealth] = useState({ state: 'loading' })

  useEffect(() => {
    let ignore = false
    apiFetch('/health/')
      .then((data) => !ignore && setHealth({ state: 'ok', data }))
      .catch((error) => !ignore && setHealth({ state: 'error', error }))
    return () => {
      ignore = true
    }
  }, [])

  return (
    <>
      <p className="muted">Хөгжүүлэлтийн орчны төлөв</p>
      <StatusList health={health} />
    </>
  )
}

function StatusList({ health }) {
  if (health.state === 'loading') {
    return <p>Шалгаж байна…</p>
  }

  // The backend answered: 200 = database ok, 503 = database unreachable.
  const answered =
    health.state === 'ok' || (health.error instanceof ApiError && health.error.status === 503)
  const databaseOk = health.state === 'ok' && health.data?.database === 'ok'

  return (
    <ul className="status-list">
      <StatusRow ok label="Frontend (React)" />
      <StatusRow
        ok={answered}
        label="Backend (Django)"
        hint={
          <>
            backend/README.md-ийн дагуу <code>python manage.py runserver</code> ажиллуулна уу.
          </>
        }
      />
      {answered && (
        <StatusRow
          ok={databaseOk}
          label="Өгөгдлийн сан (PostgreSQL)"
          hint={
            <>
              PostgreSQL ажиллаж байгаа эсэх, <code>backend/.env</code> дахь <code>DB_*</code>{' '}
              утгуудыг шалгана уу.
            </>
          }
        />
      )}
    </ul>
  )
}

function StatusRow({ ok, label, hint }) {
  return (
    <li className={ok ? 'status ok' : 'status error'}>
      <span>{ok ? '✓' : '✗'}</span> {label}
      {!ok && hint && <div className="hint">{hint}</div>}
    </li>
  )
}
