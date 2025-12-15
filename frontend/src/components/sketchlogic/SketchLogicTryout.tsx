import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api'
import Button from '../ui/Button'
import Stat from '../ui/Stat'
import Badge from '../ui/Badge'
import Dropzone from './Dropzone'
import ResultsPanel from './ResultsPanel'

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

export default function SketchLogicTryout() {
  const [online, setOnline] = useState<'CHECKING' | 'ONLINE' | 'OFFLINE'>('CHECKING')
  const [parser, setParser] = useState<'READY' | 'OFFLINE' | 'UNKNOWN'>('UNKNOWN')
  const [healthRaw, setHealthRaw] = useState<any>(null)

  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<AnalyzeResponse | null>(null)

  useEffect(() => {
    api.health()
      .then((h: any) => {
        setHealthRaw(h)
        setOnline('ONLINE')
        const ready =
          typeof h.circuit_parser_loaded === 'boolean'
            ? h.circuit_parser_loaded
            : (h.circuit_parser === 'available')
        setParser(ready ? 'READY' : 'OFFLINE')
      })
      .catch((e) => {
        setOnline('OFFLINE')
        setParser('UNKNOWN')
        setHealthRaw({ error: e?.message || String(e) })
      })
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
    if (!file) {
      setError('Pick an image first')
      return
    }
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const resp = await api.analyze(file)
      setData(resp)
    } catch (e: any) {
      setError(e.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  function irisImportStub(json: AnalysisResults) {
    // Later: hand off to IRis page/state/store.
    // For now: just confirm it’s wired.
    console.log('[IRis stub] import JSON', json)
    alert('IRis import stub: JSON is ready to be passed into the simulator.')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <Badge>Status: {online}</Badge>
          <Badge>Parser: {parser}</Badge>
        </div>

        <details className="text-sm text-slate-600">
          <summary className="cursor-pointer select-none text-slate-700">
            Health details
          </summary>
          <pre className="mt-2 max-h-48 overflow-auto rounded-xl bg-slate-50 p-3 text-xs text-slate-800">
            {JSON.stringify(healthRaw, null, 2)}
          </pre>
        </details>
      </div>

      <Dropzone file={file} onPick={setFile} onError={setError} />

      <div className="flex flex-wrap items-center gap-3">
        <Button disabled={!file || loading} onClick={analyze}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </Button>

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800">
            {error}
          </div>
        )}
      </div>

      {data && (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <Stat value={data.processing_time?.toFixed?.(2) ?? '--'} label="Processing (s)" />
            <Stat value={data.analysis_results.gates?.length ?? 0} label="Components" />
            <Stat value={connectedWiresCount} label="Connected Wires" />
          </div>

          <ResultsPanel
            processedImage={data.processed_image}
            analysis={data.analysis_results}
            onIrisImport={irisImportStub}
          />
        </>
      )}
    </div>
  )
}
