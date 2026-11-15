import { useAuth } from '../auth/AuthContext.js'

// Student's start page after login (US-01). Joined classes (US-03), exercises (US-07) and
// progress (US-12) go here.
export default function StudentDashboardPage() {
  const { user } = useAuth()

  return (
    <section>
      <h1>Сурагчийн самбар</h1>
      <p>Сайн байна уу, {user.email}!</p>
      <p className="muted">Таны элссэн ангиуд болон даалгаврууд энд харагдана.</p>
    </section>
  )
}
