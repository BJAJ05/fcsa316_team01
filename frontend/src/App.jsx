import { Route, Routes } from 'react-router'
import Layout from './components/Layout.jsx'
import RequireAuth from './components/RequireAuth.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import StudentDashboardPage from './pages/StudentDashboardPage.jsx'
import TeacherDashboardPage from './pages/TeacherDashboardPage.jsx'

// Add one <Route> per page. Pages live in src/pages/.
// Pages that need login are wrapped in <RequireAuth> (optionally with a role).
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route
          path="teacher"
          element={
            <RequireAuth role="teacher">
              <TeacherDashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="student"
          element={
            <RequireAuth role="student">
              <StudentDashboardPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
