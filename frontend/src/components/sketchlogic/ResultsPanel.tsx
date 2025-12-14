import CopyButton from '../ui/CopyButton'
import Button from '../ui/Button'

type Gate = { id?: string; connected_wires?: string[] | Record<string, unknown> }
type AnalysisResults = { gates?: Gate[]; wires?: Record<string, unknown> }

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
  processedImage,
  analysis,
  onIrisImport,
}: {
  processedImage?: string
  analysis: AnalysisResults
  onIrisImport?: (json: AnalysisResults) => void
}) {
  const jsonText = JSON.stringify(analysis, null, 2)

  return (
    <div className="space-y-4">
      {processedImage && (
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-medium text-slate-700">Labelled Image</h3>
            <a
              href={processedImage}
              download="sketchlogic_labelled.png"
              className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium hover:bg-slate-100"
            >
              Download image
            </a>
          </div>
          <img
            src={processedImage}
            alt="Labelled Image"
            className="w-full h-auto rounded-xl"
          />
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
              className="bg-white text-slate-900 border-slate-300 hover:bg-slate-50"
            >
              Download JSON
            </Button>

            {/* IRis stub hook */}
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
