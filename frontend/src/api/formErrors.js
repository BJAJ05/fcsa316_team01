import { ApiError } from './client.js'

const SERVER_UNREACHABLE = 'Сервертэй холбогдож чадсангүй. Түр хүлээгээд дахин оролдоно уу.'
const UNKNOWN_ERROR = 'Алдаа гарлаа. Дахин оролдоно уу.'

// Turns an error from apiFetch()/authFetch() into messages for a form:
//
//   catch (error) { setErrors(formErrors(error)) }
//   → { fields: { email: 'Энэ имэйл бүртгэлтэй байна.' }, general: null }
//
// DRF sends field errors as { email: ['...'] } and other errors as { detail: '...' }.
export function formErrors(error) {
  // No answer, or the backend crashed / is down (the Vite proxy answers 5xx then).
  if (!(error instanceof ApiError) || error.status >= 500) {
    return { fields: {}, general: SERVER_UNREACHABLE }
  }

  const fields = {}
  let general = null
  for (const [key, value] of Object.entries(error.data ?? {})) {
    const message = Array.isArray(value) ? value.join(' ') : String(value)
    if (key === 'detail' || key === 'non_field_errors') {
      general = message
    } else {
      fields[key] = message
    }
  }
  if (!general && Object.keys(fields).length === 0) {
    general = UNKNOWN_ERROR
  }
  return { fields, general }
}
