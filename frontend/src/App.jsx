import { Route, Routes } from 'react-router'
import Layout from './components/Layout.jsx'
import RequireAuth from './components/RequireAuth.jsx'
import AssignmentEditorPage from './pages/AssignmentEditorPage.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import SolveAssignmentPage from './pages/SolveAssignmentPage.jsx'
import StudentClassPage from './pages/StudentClassPage.jsx'
import StudentDashboardPage from './pages/StudentDashboardPage.jsx'
import StudentProgressPage from './pages/StudentProgressPage.jsx'
import SubmissionResultPage from './pages/SubmissionResultPage.jsx'
import TeacherClassPage from './pages/TeacherClassPage.jsx'
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
        <Route
          path="student/progress"
          element={
            <RequireAuth role="student">
              <StudentProgressPage />
            </RequireAuth>
          }
        />
        <Route
          path="student/classes/:classId"
          element={
            <RequireAuth role="student">
              <StudentClassPage />
            </RequireAuth>
          }
        />
        <Route
          path="teacher/classes/:classId"
          element={
            <RequireAuth role="teacher">
              <TeacherClassPage />
            </RequireAuth>
          }
        />
        <Route
          path="teacher/assignments/:assignmentId"
          element={
            <RequireAuth role="teacher">
              <AssignmentEditorPage />
            </RequireAuth>
          }
        />
        <Route
          path="student/assignments/:assignmentId"
          element={
            <RequireAuth role="student">
              <SolveAssignmentPage />
            </RequireAuth>
          }
        />
        <Route
          path="student/submissions/:submissionId"
          element={
            <RequireAuth role="student">
              <SubmissionResultPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
