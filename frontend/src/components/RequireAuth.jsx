import { Navigate, useLocation } from 'react-router'
import { useAuth } from '../auth/AuthContext.js'
import { dashboardPath } from '../auth/roles.js'

// Protects a page: logged-out users go to /login, users with another role go to their own
// dashboard. `role` is optional ('teacher' | 'student').
//
//   <Route path="teacher" element={<RequireAuth role="teacher"><TeacherDashboardPage /></RequireAuth>} />
export default function RequireAuth({ role, children }) {
  const { user, status } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return <p className="muted">Ачаалж байна…</p>
  }
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  if (role && user.role !== role) {
    return <Navigate to={dashboardPath(user.role)} replace />
  }
  return children
}
