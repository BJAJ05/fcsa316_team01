// User roles, the same values as the backend (accounts.User.Role).
export const ROLE_LABELS = {
  teacher: 'Багш',
  student: 'Сурагч',
}

// Each role has its own dashboard page (see App.jsx).
export function dashboardPath(role) {
  return role === 'teacher' ? '/teacher' : '/student'
}
