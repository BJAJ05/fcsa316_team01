import { useAuth } from '../auth/AuthContext.js'

// Teacher's start page after login (US-01). Classes (US-02, US-04) and reports (US-13) go here.
export default function TeacherDashboardPage() {
  const { user } = useAuth()

  return (
    <section>
      <h1>Багшийн самбар</h1>
      <p>Сайн байна уу, {user.email}!</p>
      <p className="muted">Таны үүсгэсэн ангиуд энд харагдана.</p>
    </section>
  )
}
