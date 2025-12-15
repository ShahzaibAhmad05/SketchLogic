import { useState } from 'react'
import Button from './Button'

export default function CopyButton({
  getText,
  label = 'Copy',
  className = '',
}: {
  getText: () => string
  label?: string
  className?: string
}) {
  const [state, setState] = useState<'IDLE' | 'COPIED' | 'FAILED'>('IDLE')

  async function copy() {
    try {
      const text = getText()
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text)
      } else {
        // fallback
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.left = '-9999px'
        document.body.appendChild(ta)
        ta.focus()
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
      }
      setState('COPIED')
      setTimeout(() => setState('IDLE'), 1200)
    } catch {
      setState('FAILED')
      setTimeout(() => setState('IDLE'), 1200)
    }
  }

  return (
    <Button
      type="button"
      onClick={copy}
      className={`bg-black text-slate-900 border-slate-300 hover:bg-slate-50 ${className}`}
    >
      {state === 'COPIED' ? 'Copied ✓' : state === 'FAILED' ? 'Copy failed' : label}
    </Button>
  )
}
