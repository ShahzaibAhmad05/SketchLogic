// api.ts
export type HealthResponse = {
  status: string
  circuit_parser_loaded?: boolean
  circuit_parser?: string
  timestamp?: number
}

export type Gate = { id?: string; connected_wires?: string[] | Record<string, unknown> }
export type AnalysisResults = { gates?: Gate[]; wires?: Record<string, unknown> }
export type AnalyzeResponse = {
  success: boolean
  processing_time?: number
  analysis_results: AnalysisResults
  original_image?: string
  processed_image?: string
  filename?: string
  timestamp?: number
}

let API_BASE = import.meta.env.VITE_API_BASE || '/api';
// Ensure it ends with /api
if (!API_BASE.endsWith('/api')) {
  API_BASE = API_BASE.replace(/\/+$/, '') + '/api';
}

async function toJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  const data = (() => { try { return JSON.parse(text) } catch { return null } })();
  if (!res.ok) {
    const msg = (data && (data.error || data.details)) || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return (data as T);
}

export const api = {
  health: (): Promise<HealthResponse> =>
    fetch(`${API_BASE}/health`).then((r) => toJson<HealthResponse>(r)),

  analyze: (file: File): Promise<AnalyzeResponse> => {
    const fd = new FormData();
    fd.append('image', file);
    return fetch(`${API_BASE}/process-circuit`, { method: 'POST', body: fd })
      .then((r) => toJson<AnalyzeResponse>(r));
  },
};
