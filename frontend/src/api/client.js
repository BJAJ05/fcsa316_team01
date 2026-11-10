// All requests to the Django backend go through apiFetch().
// Paths are relative to /api and end with a slash, like the Django URLs.
//
//   const data = await apiFetch('/health/')
//   await apiFetch('/classes/join/', { method: 'POST', body: { code: 'AB12CD' }, token })
//
// In development Vite forwards /api to Django (see vite.config.js).

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export class ApiError extends Error {
  constructor(status, data) {
    super(`API request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    // Parsed JSON error body from Django/DRF, e.g. { email: ['...'] }, or null.
    this.data = data
  }
}

export async function apiFetch(path, { method = 'GET', body, token, headers = {} } = {}) {
  const requestHeaders = { Accept: 'application/json', ...headers }
  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`
  }

  let requestBody
  if (body instanceof FormData) {
    // File uploads: the browser sets the multipart Content-Type itself.
    requestBody = body
  } else if (body !== undefined) {
    requestHeaders['Content-Type'] = 'application/json'
    requestBody = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: requestHeaders,
    body: requestBody,
  })

  const data = await readJson(response)
  if (!response.ok) {
    throw new ApiError(response.status, data)
  }
  return data
}

async function readJson(response) {
  const text = await response.text()
  if (!text) {
    return null
  }
  try {
    return JSON.parse(text)
  } catch {
    // Not JSON (e.g. an HTML error page); keep the raw text for debugging.
    return { detail: text }
  }
}
