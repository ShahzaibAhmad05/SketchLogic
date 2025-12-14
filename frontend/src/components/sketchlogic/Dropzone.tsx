import { useRef } from 'react'
import Card from '../ui/Card'

export default function Dropzone({
  file,
  onPick,
  onError,
}: {
  file: File | null
  onPick: (file: File) => void
  onError: (msg: string) => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFile(f?: File) {
    if (!f) return
    if (f.type.startsWith('image/')) onPick(f)
    else onError('Invalid file type')
  }

  return (
    <Card
      className="cursor-pointer p-6 text-center hover:bg-slate-50 transition"
      // drag/drop
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        handleFile(e.dataTransfer.files?.[0])
      }}
      // click
      onClick={() => inputRef.current?.click()}
    >
      <p className="text-slate-700">Drop an image or click to browse</p>
      <p className="mt-1 text-sm text-slate-500">
        JPG / PNG / WebP supported
      </p>

      <input
        ref={inputRef}
        type="file"
        hidden
        accept="image/*"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      {file && <p className="mt-3 text-sm text-slate-600">Selected: {file.name}</p>}
    </Card>
  )
}
