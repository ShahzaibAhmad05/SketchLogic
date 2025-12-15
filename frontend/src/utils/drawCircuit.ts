// src/utils/drawCircuit.ts
import type { AnalysisResults, Gate, WirePoint } from '../api'

export type DrawCircuitOptions = {
  fontSize?: number // -1 = auto
  wireWidth?: number
  bottomGap?: number
  bgPad?: number
  gateOutlineColor?: string // CSS color
  gateOutlineWidth?: number
  drawWirePoints?: boolean
  wirePointRadius?: number
  wireColor?: string
  wirePointColor?: string
  textColor?: string
}

const DEFAULTS: Required<DrawCircuitOptions> = {
  fontSize: -1,
  wireWidth: 5,
  bottomGap: 6,
  bgPad: 4,
  gateOutlineColor: 'rgba(0,255,0,1)',
  gateOutlineWidth: 6,
  drawWirePoints: true,
  wirePointRadius: 3,
  wireColor: 'rgba(255,0,0,1)',
  wirePointColor: 'rgba(0,0,255,1)',
  textColor: 'rgba(0,0,0,1)',
}

function toFiniteNumber(v: unknown): number | null {
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) ? n : null
}

function toInt(v: unknown, fallback = 0): number {
  const n = toFiniteNumber(v)
  return n === null ? fallback : Math.trunc(n)
}

function normalizeWirePoints(raw: unknown): WirePoint[] {
  if (!Array.isArray(raw)) return []
  const pts: WirePoint[] = []
  for (const p of raw) {
    if (!Array.isArray(p) || p.length !== 2) continue
    const x = toFiniteNumber(p[0])
    const y = toFiniteNumber(p[1])
    if (x === null || y === null) continue
    pts.push([Math.trunc(x), Math.trunc(y)])
  }
  return pts
}

export function drawCircuitOnCanvas(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  analysis: AnalysisResults,
  opts: DrawCircuitOptions = {}
) {
  const o = { ...DEFAULTS, ...opts }

  const imgW = img.naturalWidth || img.width
  const imgH = img.naturalHeight || img.height

  // Reset any prior transforms/styles to avoid “drifting” issues across draws
  ctx.save()
  try {
    // Clear + base image
    ctx.clearRect(0, 0, imgW, imgH)
    ctx.drawImage(img, 0, 0, imgW, imgH)

    // Auto font sizing (match your Pillow approach)
    let fontSize = o.fontSize
    let bgPad = o.bgPad
    if (fontSize === -1) {
      fontSize = Math.max(10, Math.floor(imgW * 0.02))
      bgPad = Math.max(2, Math.floor(fontSize * 0.2))
    }

    ctx.font = `${fontSize}px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial`
    ctx.textBaseline = 'top'

    //
    // 1) Gates (green boxes + label background + black text)
    //
    const gates = (analysis?.gates ?? []) as Gate[]
    ctx.lineJoin = 'miter'
    ctx.lineCap = 'butt'

    for (const gate of gates) {
      const x = toInt((gate as any).x)
      const y = toInt((gate as any).y)
      const w = toInt((gate as any).width)
      const h = toInt((gate as any).height)
      if (w <= 0 || h <= 0) continue

      const gateType = (gate as any).type ?? 'Unknown'
      const rotation = toInt((gate as any).rotation)
      const label = `${gateType} @ ${rotation}°`

      // Outline rectangle
      ctx.strokeStyle = o.gateOutlineColor
      ctx.lineWidth = o.gateOutlineWidth
      ctx.strokeRect(x, y, w, h)

      // Measure label
      const textMetrics = ctx.measureText(label)
      const tw = Math.ceil(textMetrics.width)
      const th = Math.ceil(fontSize)

      // Background box like your Pillow logic (bottom-center)
      const bgW = tw + 2 * bgPad
      const bgH = th + 2 * bgPad
      const centerX = x + w / 2

      const bgLeft = Math.floor(centerX - bgW / 2)
      const bgBottom = y + h - o.bottomGap
      const bgTop = bgBottom - bgH

      // Background
      ctx.fillStyle = o.gateOutlineColor
      ctx.fillRect(bgLeft, bgTop, bgW, bgH)

      // Text
      const tx = Math.floor(bgLeft + (bgW - tw) / 2)
      const ty = Math.floor(bgTop + (bgH - th) / 2)
      ctx.fillStyle = o.textColor
      ctx.fillText(label, tx, ty)
    }

    //
    // 2) Wires (red polylines + optional blue points)
    //
    const wires = analysis?.wires
    if (wires && typeof wires === 'object') {
      ctx.strokeStyle = o.wireColor
      ctx.lineWidth = o.wireWidth
      ctx.lineJoin = 'round'
      ctx.lineCap = 'round'

      for (const rawPoints of Object.values(wires as Record<string, unknown>)) {
        const pts = normalizeWirePoints(rawPoints)

        // your backend may include [] for some wires
        if (pts.length < 2) continue

        ctx.beginPath()
        ctx.moveTo(pts[0][0], pts[0][1])
        for (let i = 1; i < pts.length; i++) {
          ctx.lineTo(pts[i][0], pts[i][1])
        }
        ctx.stroke()

        if (o.drawWirePoints) {
          ctx.fillStyle = o.wirePointColor
          const r = o.wirePointRadius
          for (const [px, py] of pts) {
            ctx.beginPath()
            ctx.arc(px, py, r, 0, Math.PI * 2)
            ctx.fill()
          }
        }
      }
    }
  } finally {
    ctx.restore()
  }
}
