import { useEffect, useMemo, useRef, useState } from 'react'
import type { AnalysisResults } from '../../api'
import { drawCircuitOnCanvas, type DrawCircuitOptions } from '../../utils/drawCircuit'

function downloadCanvasPng(canvas: HTMLCanvasElement, filename: string) {
  canvas.toBlob((blob) => {
    if (!blob) return
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }, 'image/png')
}

export default function LabeledCanvas({
  file,
  analysis,
  options,
}: {
  file: File
  analysis: AnalysisResults
  options?: DrawCircuitOptions
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const imgRef = useRef<HTMLImageElement | null>(null)
  const [imgLoaded, setImgLoaded] = useState(false)

  const url = useMemo(() => URL.createObjectURL(file), [file])
  useEffect(() => () => URL.revokeObjectURL(url), [url])

  useEffect(() => {
    const img = imgRef.current
    const canvas = canvasRef.current
    if (!img || !canvas || !imgLoaded) return

    const w = img.naturalWidth || img.width
    const h = img.naturalHeight || img.height

    // HiDPI crispness
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.floor(w * dpr)
    canvas.height = Math.floor(h * dpr)
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`

    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

    drawCircuitOnCanvas(ctx, img, analysis, options)
  }, [analysis, imgLoaded, options])

  return (
    <div className="space-y-3">
      <img
        ref={imgRef}
        src={url}
        alt="Uploaded circuit"
        className="hidden"
        onLoad={() => setImgLoaded(true)}
      />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-medium text-slate-700">Labelled Image</h3>
        <button
          type="button"
          onClick={() => {
            const c = canvasRef.current
            if (c) downloadCanvasPng(c, 'sketchlogic_labelled.png')
          }}
          className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium hover:bg-slate-100"
        >
          Download image
        </button>
      </div>

      <div className="overflow-auto">
        <canvas ref={canvasRef} className="max-w-full rounded-xl" />
      </div>
    </div>
  )
}
