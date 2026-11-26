import { useState } from 'react'

// A class's join code with a "Хуулах" (copy) button, for sharing with students (US-02, US-04).
//
//   <ClassCode code={classroom.code} />
export default function ClassCode({ code }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // The clipboard is only available on https or localhost; the code stays visible to copy.
    }
  }

  return (
    <span className="class-code">
      <code>{code}</code>
      <button type="button" className="button secondary" onClick={handleCopy}>
        {copied ? 'Хуулсан' : 'Хуулах'}
      </button>
    </span>
  )
}
