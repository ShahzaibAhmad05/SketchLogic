import CopyButton from '../ui/CopyButton'
import Button from '../ui/Button'
import type { AnalysisResults } from '../../api'
import LabeledCanvas from './LabeledCanvas'

// type Gate = { id?: string; connected_wires?: string[] | Record<string, unknown> }

function downloadText(filename: string, text: string) {
  const blob = new Blob([text], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function ResultsPanel({
  file,
  analysis,
  onIrisImport,
}: {
  file?: File | null
  analysis: AnalysisResults
  onIrisImport?: (json: AnalysisResults) => void
}) {
  const jsonText = JSON.stringify(analysis, null, 2)

  return (
    <div className="space-y-4">
      {file && (
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          {/* LabeledCanvas already contains the Download button and renders the canvas */}
          <LabeledCanvas file={file} analysis={analysis} />
        </div>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-medium text-slate-700">JSON Output</h3>
          <div className="flex flex-wrap gap-2">
            <CopyButton getText={() => jsonText} label="Copy JSON" />
            <Button
              type="button"
              onClick={() => downloadText('sketchlogic_results.json', jsonText)}
              className="bg-black text-slate-900 border-slate-300 hover:bg-slate-50"
            >
              Download JSON
            </Button>

            {onIrisImport && (
              <Button type="button" onClick={() => onIrisImport(analysis)}>
                Import into IRis (stub)
              </Button>
            )}
          </div>
        </div>

        <pre className="max-h-[420px] overflow-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-800">
          {jsonText}
        </pre>
      </div>
    </div>
  )
}
