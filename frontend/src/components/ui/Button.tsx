import type { ButtonHTMLAttributes } from 'react'

export default function Button({
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={[
        'inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium',
        'border border-slate-300 bg-slate-900 text-white hover:bg-slate-800',
        'disabled:cursor-not-allowed disabled:opacity-60',
        className,
      ].join(' ')}
    />
  )
}
