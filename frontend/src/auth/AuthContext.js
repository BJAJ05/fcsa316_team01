import { createContext, useContext } from 'react'

export const AuthContext = createContext(null)

// Logged-in user and auth actions, provided by <AuthProvider> (main.jsx):
//
//   const { user, status, login, register, logout, authFetch } = useAuth()
//
// user      — { id, email, role } or null when logged out
// status    — 'loading' while a saved session is being checked, then 'ready'
// authFetch — apiFetch() that sends the user's token (use it for every API call that needs login)
export function useAuth() {
  const auth = useContext(AuthContext)
  if (!auth) {
    throw new Error('useAuth() must be used inside <AuthProvider>.')
  }
  return auth
}
