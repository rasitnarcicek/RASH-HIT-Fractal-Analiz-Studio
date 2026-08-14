/**
 * RASH-HIT Fractal Studio - API Client Layer
 * STRICT RULE: ONLY api.js executes HTTP/REST requests (fetch/XHR).
 *
 * Contract:
 *   runSingleAnalysis(formData)        -> POST /api/upload-single  (multipart: file, levels, mode)
 *   runBatchAnalysis(formData)         -> POST /api/upload-batch   (multipart: files[], levels, mode)
 *   runSingleAnalysisByPath(path, lv)  -> POST /api/analyze        (JSON path-based fallback)
 *   runBatchAnalysisByPath(folder, lv) -> POST /api/batch          (JSON path-based fallback)
 *
 * Multipart bodies are passed as-is (FormData). The browser generates the
 * boundary automatically, so NO manual Content-Type header must be set.
 */
const API = {

  async getHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) return await res.json();
    } catch (e) {}
    return null;
  },

  async getJobStatus(jobId) {
    try {
      const res = await fetch('/api/jobs/' + jobId);
      if (res.ok) return await res.json();
    } catch (e) {}
    return null;
  },

  /** Run-history summary (newest first) - feeds the Analysis Studio history panel. */
  async getJobs() {
    try {
      const res = await fetch('/api/jobs');
      if (res.ok) return await res.json();
    } catch (e) {}
    return { jobs: [] };
  },

  async getPackages() {
    try {
      const res = await fetch('/api/packages');
      if (res.ok) {
        const data = await res.json();
        return Array.isArray(data) ? { packages: data } : data;
      }
    } catch (e) {
      try {
        const res2 = await fetch('./package_index.json');
        if (res2.ok) {
          const data = await res2.json();
          return Array.isArray(data) ? { packages: data } : data;
        }
      } catch (err) {}
    }
    return { packages: [] };
  },

  async getStats() {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) return await res.json();
    } catch (e) {}
    return null;
  },

  /** Fetch one package record by package id / folder name. */
  async getPackage(packageId) {
    try {
      const res = await fetch('/api/package/' + encodeURIComponent(packageId));
      if (res.ok) return await res.json();
    } catch (e) {}
    return null;
  },

  /** Open a package folder in the OS file explorer (via the local server). */
  async openFolder(packageId) {
    try {
      const res = await fetch('/api/open-folder/' + encodeURIComponent(packageId));
      return await res.json();
    } catch (e) {}
    return { error: 'Folder open request failed' };
  },

  async deletePackages(packageIds) {
    const res = await fetch('/api/packages/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ package_ids: packageIds })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || 'Delete operation failed');
    }
    return await res.json();
  },

  /**
   * Single SVG analysis from a real File object.
   * @param {FormData} formData - fields: file (File), levels, mode (optional)
   */
  async runSingleAnalysis(formData) {
    const res = await fetch('/api/upload-single', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || 'Single analysis failed');
    }
    return await res.json();
  },

  /**
   * Batch SVG analysis from real File objects.
   * @param {FormData} formData - fields: files[] (File, repeated), levels, mode (optional)
   */
  async runBatchAnalysis(formData) {
    const res = await fetch('/api/upload-batch', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || 'Batch analysis failed');
    }
    return await res.json();
  },

  /** Legacy path-based single analysis (JSON). Kept for terminal/backward compat. */
  async runSingleAnalysisByPath(inputPath, levels) {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_path: inputPath, levels: levels })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || 'Single analysis failed');
    }
    return await res.json();
  },

  /** Legacy path-based batch analysis (JSON). Kept for terminal/backward compat. */
  async runBatchAnalysisByPath(folderPath, levels) {
    const res = await fetch('/api/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: folderPath, levels: levels })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || 'Batch analysis failed');
    }
    return await res.json();
  },

};
