// script.js
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  // Cache DOM
  const els = {
    imageFile: document.getElementById('imageFile'),
    fileName: document.getElementById('fileName'),
    uploadBtn: document.getElementById('uploadBtn'),
    loading: document.getElementById('loading'),
    results: document.getElementById('results'),
    error: document.getElementById('error'),
    dragDropArea: document.getElementById('dragDropArea'),
    serverStatus: document.getElementById('serverStatus'),
    parserStatus: document.getElementById('parserStatus'),
    processingTime: document.getElementById('processingTime'),
    processingTimeStat: document.getElementById('processingTimeStat'),
    componentsCount: document.getElementById('componentsCount'),
    wiresCount: document.getElementById('wiresCount'),
    jsonContainer: document.getElementById('jsonContainer'),
    copyBtn: document.getElementById('copyBtn')
  };

  // If the frontend is served by the same Flask app, keep empty to use same-origin
  const API_BASE = '';

  let selectedFile = null;
  let analysisData = null;

  // ---------- UI helpers ----------
  function showLoading() {
    els.loading.style.display = 'block';
    els.uploadBtn.disabled = true;
  }
  function hideLoading() {
    els.loading.style.display = 'none';
    els.uploadBtn.disabled = !selectedFile;
  }
  function showResults() {
    els.results.style.display = 'block';
  }
  function hideResults() {
    els.results.style.display = 'none';
  }
  function showError(message) {
    els.error.textContent = message;
    els.error.style.display = 'block';
  }
  function hideError() {
    els.error.style.display = 'none';
  }
  function setStatus({ online, parserReady }) {
    els.serverStatus.textContent = online ? 'ONLINE' : 'OFFLINE';
    els.parserStatus.textContent = parserReady ? 'READY' : (online ? 'OFFLINE' : 'UNKNOWN');
  }

  // ---------- JSON rendering (with preserved indentation) ----------
  function syntaxHighlightJson(json) {
    const safe = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return safe.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = 'json-number';
        if (/^"/.test(match)) {
          cls = /:$/.test(match) ? 'json-key' : 'json-string';
        } else if (/true|false/.test(match)) {
          cls = 'json-boolean';
        } else if (/null/.test(match)) {
          cls = 'json-null';
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );
  }

  function displayJsonData(data) {
    const jsonString = JSON.stringify(data, null, 2); // <-- pretty-print with 2 spaces
    // Render inside a <pre> so whitespace/indentation is preserved
    const pre = document.createElement('pre');
    pre.className = 'json-pre';
    // Inline styles in case CSS doesn't define them
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.wordBreak = 'break-word';
    pre.style.margin = '0';
    pre.style.fontFamily = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace';
    pre.style.fontSize = '0.9rem';
    pre.style.lineHeight = '1.4';

    // With syntax highlight (optional). If you don't want colors, use: pre.textContent = jsonString;
    pre.innerHTML = syntaxHighlightJson(jsonString);

    els.jsonContainer.replaceChildren(pre);
  }

  // ---------- Server status ----------
  async function checkServerStatus() {
    setStatus({ online: false, parserReady: false });
    try {
      const res = await fetch(`${API_BASE}/health`, { method: 'GET' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setStatus({ online: true, parserReady: !!data.circuit_parser_loaded });

      console.log(!data.circuit_parser_loaded)
      if (!data.circuit_parser_loaded) {
        showError('Circuit analysis service is not available. Please check server logs.');
      } else {
        hideError();
      }
    } catch {
      setStatus({ online: false, parserReady: false });
      showError('Cannot connect to analysis server. Please ensure the server is running.');
    }
  }

  // ---------- File selection ----------
  function handleFileSelect(file) {
    if (file && file.type && file.type.startsWith('image/')) {
      selectedFile = file;
      els.fileName.textContent = `> ${file.name}`;
      els.uploadBtn.disabled = false;
      hideError();
      hideResults();
    } else if (file) {
      selectedFile = null;
      els.fileName.textContent = '';
      els.uploadBtn.disabled = true;
      showError('Invalid file type. Please select a circuit diagram image.');
    }
  }

  // File input change
  els.imageFile.addEventListener('change', (e) => {
    handleFileSelect(e.target.files && e.target.files[0]);
  });

  // Click to browse (on button or whole drop area)
  const browseBtn = document.querySelector('.file-input-wrapper .btn');
  if (browseBtn) {
    browseBtn.addEventListener('click', (e) => {
      e.preventDefault();
      els.imageFile.click();
    });
  }
  els.dragDropArea.addEventListener('click', (e) => {
    if (!(e.target && e.target.closest('.file-input-wrapper'))) {
      els.imageFile.click();
    }
  });

  // Drag & drop
  els.dragDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    els.dragDropArea.classList.add('dragover');
  });
  els.dragDropArea.addEventListener('dragleave', () => {
    els.dragDropArea.classList.remove('dragover');
  });
  els.dragDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    els.dragDropArea.classList.remove('dragover');
    const files = e.dataTransfer && e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  });

  // ---------- Upload & analyze ----------
  els.uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
      showError('Please select a circuit diagram first.');
      return;
    }

    hideResults();
    hideError();
    showLoading();

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const res = await fetch(`${API_BASE}/process-circuit`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const message = (data && (data.error || data.details)) || `Server error: ${res.status}`;
        throw new Error(message);
      }

      // Success
      analysisData = data;

      // Processing time
      const t = typeof data.processing_time === 'number' ? data.processing_time : null;
      const tStr = t !== null ? `${t.toFixed(2)}s` : '--';
      els.processingTime.textContent = tStr;
      els.processingTimeStat.textContent = t !== null ? t.toFixed(2) : '--';

      // Counts (defensive)
      const results = data.analysis_results || {};
      const gates = Array.isArray(results.gates) ? results.gates : [];
      const wires = Array.isArray(results.wires) ? results.wires : [];
      els.componentsCount.textContent = String(gates.length);
      els.wiresCount.textContent = String(wires.length);

      // Images (data URLs expected from server)
      const origImg = document.getElementById('originalImage');
      const procImg = document.getElementById('processedImage');
      if (data.original_image) origImg.src = data.original_image;
      if (data.processed_image) procImg.src = data.processed_image;

      // JSON panel (properly indented)
      displayJsonData(results);

      showResults();
    } catch (err) {
      showError(`Circuit analysis failed: ${err.message || err}`);
    } finally {
      hideLoading();
    }
  });

  // ---------- Copy JSON ----------
  els.copyBtn.addEventListener('click', async () => {
    if (!analysisData || !analysisData.analysis_results) return;
    const jsonText = JSON.stringify(analysisData.analysis_results, null, 2);
    try {
      await navigator.clipboard.writeText(jsonText);
      els.copyBtn.textContent = 'COPIED!';
      setTimeout(() => (els.copyBtn.textContent = 'COPY JSON'), 2000);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = jsonText;
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        els.copyBtn.textContent = 'COPIED!';
        setTimeout(() => (els.copyBtn.textContent = 'COPY JSON'), 2000);
      } finally {
        document.body.removeChild(ta);
      }
    }
  });

  // ---------- Init ----------
  els.uploadBtn.disabled = true;
  hideResults();
  hideError();
  checkServerStatus();
});
