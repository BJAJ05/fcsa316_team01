import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ApiError, apiFetch } from '../api/client.js'
import { AuthContext } from './AuthContext.js'

// The JWT pair is kept in localStorage so the user stays logged in after a page reload.
const STORAGE_KEY = 'lms.auth'

function readTokens() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY))
    return saved?.access && saved?.refresh ? saved : null
  } catch {
    return null
  }
}

function writeTokens(tokens) {
  try {
    if (tokens) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    // Storage blocked (e.g. private mode): login still works, it just won't survive a reload.
  }
}

export default function AuthProvider({ children }) {
  const [initialTokens] = useState(readTokens)
  const tokens = useRef(initialTokens)
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState(initialTokens ? 'loading' : 'ready')

  const saveSession = useCallback(({ user, access, refresh }) => {
    tokens.current = { access, refresh }
    writeTokens(tokens.current)
    setUser(user)
    return user
  }, [])

  const logout = useCallback(() => {
    tokens.current = null
    writeTokens(null)
    setUser(null)
  }, [])

  // Gets a new access token (they live 60 min). Returns false if the refresh token is no good.
  const refreshAccessToken = useCallback(async () => {
    const refresh = tokens.current?.refresh
    if (!refresh) {
      return false
    }
    try {
      const { access } = await apiFetch('/auth/refresh/', { method: 'POST', body: { refresh } })
      tokens.current = { ...tokens.current, access }
      writeTokens(tokens.current)
      return true
    } catch (error) {
      if (error instanceof ApiError) {
        return false
      }
      throw error // network problem: keep the session, let the caller show the error
    }
  }, [])

  // apiFetch() with the access token. On 401 it refreshes the token once and retries;
  // if the session cannot be renewed the user is logged out and the error is rethrown.
  const authFetch = useCallback(
    async (path, options = {}) => {
      const send = () => apiFetch(path, { ...options, token: tokens.current?.access })
      try {
        return await send()
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 401) {
          throw error
        }
        if (!(await refreshAccessToken())) {
          logout()
          throw error
        }
        return send()
      }
    },
    [refreshAccessToken, logout],
  )

  const login = useCallback(
    async (email, password) =>
      saveSession(await apiFetch('/auth/login/', { method: 'POST', body: { email, password } })),
    [saveSession],
  )

  const register = useCallback(
    async (email, password, role) =>
      saveSession(
        await apiFetch('/auth/register/', { method: 'POST', body: { email, password, role } }),
      ),
    [saveSession],
  )

  // After a reload: tokens were saved, so ask the backend who is logged in.
  useEffect(() => {
    if (!initialTokens) {
      return
    }
    let ignore = false
    authFetch('/auth/me/')
      .then((me) => {
        if (!ignore) setUser(me)
      })
      .catch(() => {
        // Expired session (authFetch already logged out) or backend unreachable.
      })
      .finally(() => {
        if (!ignore) setStatus('ready')
      })
    return () => {
      ignore = true
    }
  }, [initialTokens, authFetch])

  const value = useMemo(
    () => ({ user, status, login, register, logout, authFetch }),
    [user, status, login, register, logout, authFetch],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
