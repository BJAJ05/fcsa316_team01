import { Link, NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../auth/AuthContext.js'
import { ROLE_LABELS } from '../auth/roles.js'

// Shared page frame: header on top, the current page below.
export default function Layout() {
  const { user, status, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <>
      <header className="site-header">
        <Link to="/" className="brand">
          LMS
        </Link>
        {status === 'ready' && (
          <nav className="site-nav">
            {user ? (
              <>
                <span className="muted">
                  {user.email} · {ROLE_LABELS[user.role]}
                </span>
                <button type="button" className="button secondary" onClick={handleLogout}>
                  Гарах
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login">Нэвтрэх</NavLink>
                <NavLink to="/register">Бүртгүүлэх</NavLink>
              </>
            )}
          </nav>
        )}
      </header>
      <main className="page">
        <Outlet />
      </main>
    </>
  )
}
