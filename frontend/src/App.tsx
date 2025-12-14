import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api'
import banner from './assets/banner.jpg'

type Gate = { id?: string; connected_wires?: string[] | Record<string, unknown> }
type AnalysisResults = { gates?: Gate[]; wires?: Record<string, unknown> }
type AnalyzeResponse = {
  success: boolean
  processing_time?: number
  analysis_results: AnalysisResults
  original_image?: string
  processed_image?: string
  filename?: string
  timestamp?: number
}

export default function App() {
  const [online, setOnline] = useState<'CHECKING'|'ONLINE'|'OFFLINE'>('CHECKING')
  const [parser, setParser] = useState<'READY'|'OFFLINE'|'UNKNOWN'>('UNKNOWN')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<AnalyzeResponse | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    document.title = 'SketchLogic'
    api.health()
      .then((h: any) => {
        setOnline('ONLINE')
        const ready = typeof h.circuit_parser_loaded === 'boolean'
          ? h.circuit_parser_loaded
          : (h.circuit_parser === 'available')
        setParser(ready ? 'READY' : 'OFFLINE')
      })
      .catch(() => { setOnline('OFFLINE'); setParser('UNKNOWN') })
  }, [])

  const connectedWiresCount = useMemo(() => {
    const gates = data?.analysis_results?.gates || []
    return gates.reduce((acc, g) => {
      const cw = (g as any).connected_wires
      if (Array.isArray(cw)) return acc + cw.length
      if (cw && typeof cw === 'object') return acc + Object.keys(cw).length
      return acc
    }, 0)
  }, [data])

  async function analyze() {
    if (!file) { setError('Pick an image first'); return }
    setLoading(true); setError(null); setData(null)
    try {
      const resp = await api.analyze(file)
      setData(resp)
    } catch (e: any) {
      setError(e.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
      <div className="w-full max-w-4xl">
        <header className="text-center">
          <img
            src={banner}
            alt="SketchLogic banner"
            className="mx-auto mb-4 w-full max-w-[560px] md:max-w-[720px] lg:max-w-[880px] select-none"
          />

          <p className="text-slate-400 mt-1">
            Status: <b>{online}</b> &nbsp;|&nbsp; Parser: <b>{parser}</b>
          </p>
        </header>

        <section className="mt-6">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault()
              const f = e.dataTransfer.files?.[0]
              if (f && f.type.startsWith('image/')) setFile(f); else setError('Invalid file type')
            }}
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-slate-600 rounded-xl p-6 text-center cursor-pointer hover:bg-slate-900 transition"
          >
            <p className="text-slate-300">Drop image or click to browse</p>
            <input
              ref={inputRef}
              type="file"
              hidden
              accept="image/*"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f && f.type.startsWith('image/')) setFile(f); else setError('Invalid file type')
              }}
            />
          </div>

          {file && <p className="text-slate-400 mt-2">Selected: {file.name}</p>}

          <button
            disabled={!file || loading}
            onClick={analyze}
            className="mt-3 inline-flex items-center justify-center rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 font-medium hover:bg-slate-700 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing…' : 'Analyze'}
          </button>

          {error && <div className="text-rose-400 mt-3">{error}</div>}
        </section>

        {data && (
          <section className="mt-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-slate-900/60 rounded-lg p-3 text-center">
                <div className="text-lg font-bold">{data.processing_time?.toFixed?.(2) ?? '--'}</div>
                <div className="text-slate-400 text-sm">Processing (s)</div>
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 text-center">
                <div className="text-lg font-bold">{data.analysis_results.gates?.length ?? 0}</div>
                <div className="text-slate-400 text-sm">Components</div>
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 text-center">
                <div className="text-lg font-bold">{connectedWiresCount}</div>
                <div className="text-slate-400 text-sm">Connected Wires</div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-1 gap-3">
              {data.processed_image && (
                <div className="bg-slate-900/60 rounded-lg p-3">
                  <h3 className="mb-2 font-medium text-slate-300">Labelled Image</h3>
                  <img src={data.processed_image} alt="Labelled Image" className="w-full h-auto rounded-md" />
                </div>
              )}
            </div>

            <pre className="json-pre bg-slate-900/60 text-slate-100 p-4 rounded-lg max-h-[400px] overflow-auto">
              {JSON.stringify(data.analysis_results, null, 2)}
            </pre>
          </section>
        )}
      </div>
    </main>
  )
}
