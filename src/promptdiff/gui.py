"""Web-based graphical interface for promptdiff powered by Flask.

Launch with::

    promptdiff-gui               # opens http://localhost:5000 in a browser
    promptdiff-gui --port 8080   # custom port
    promptdiff-gui --no-browser  # skip auto-opening

Requires the optional ``gui`` extra::

    pip install promptdiff[gui]
"""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser

try:
    from flask import Flask, jsonify, render_template_string, request
except ImportError as _exc:  # pragma: no cover
    raise ImportError(
        "The GUI requires Flask. Install it with:  pip install promptdiff[gui]"
    ) from _exc

from promptdiff import diff, format_unified, similarity, word_diff

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>promptdiff</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: #f8f9fa;
    color: #212529;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    background: #343a40;
    color: #fff;
    padding: 12px 24px;
    display: flex;
    align-items: baseline;
    gap: 12px;
  }
  header h1 { font-size: 1.25rem; font-weight: 600; letter-spacing: 0.5px; }
  header small { font-size: 0.8rem; color: #adb5bd; }
  main { flex: 1; padding: 16px 24px; display: flex; flex-direction: column; gap: 12px; }

  /* Input panels */
  .inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .panel label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #495057;
    margin-bottom: 4px;
  }
  textarea {
    width: 100%;
    height: 160px;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.85rem;
    resize: vertical;
    background: #fff;
  }
  textarea:focus { outline: none; border-color: #80bdff; box-shadow: 0 0 0 3px rgba(0,123,255,.25); }

  /* Controls */
  .controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  button {
    padding: 7px 16px;
    border: none;
    border-radius: 5px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
  }
  .btn-primary { background: #0d6efd; color: #fff; }
  .btn-primary:hover { background: #0b5ed7; }
  .btn-secondary { background: #6c757d; color: #fff; }
  .btn-secondary:hover { background: #5a6268; }
  .btn-outline { background: #fff; color: #495057; border: 1px solid #ced4da; }
  .btn-outline:hover { background: #e9ecef; }
  #similarity-badge {
    margin-left: auto;
    padding: 5px 14px;
    background: #e9ecef;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
    color: #495057;
    min-width: 160px;
    text-align: center;
  }
  #similarity-badge.high   { background: #d4edda; color: #155724; }
  #similarity-badge.medium { background: #fff3cd; color: #856404; }
  #similarity-badge.low    { background: #f8d7da; color: #721c24; }

  /* Output */
  .output-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .output-header h2 { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #495057; }
  #mode-label { font-size: 0.75rem; color: #6c757d; }
  #output {
    flex: 1;
    min-height: 200px;
    background: #fff;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 10px 12px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }
  #output:empty::before { content: "Diff output will appear here…"; color: #adb5bd; }
  .op-add    { background: #d4edda; color: #155724; display: block; }
  .op-remove { background: #f8d7da; color: #721c24; display: block; }
  .op-equal  { color: #495057; display: block; }
  /* word diff: inline spans */
  .w-add    { background: #d4edda; color: #155724; border-radius: 2px; padding: 0 2px; }
  .w-remove { background: #f8d7da; color: #721c24; border-radius: 2px; padding: 0 2px; text-decoration: line-through; }

  #toast {
    position: fixed; bottom: 24px; right: 24px;
    background: #343a40; color: #fff;
    padding: 10px 18px; border-radius: 6px;
    font-size: 0.875rem;
    opacity: 0; pointer-events: none;
    transition: opacity 0.25s;
  }
  #toast.show { opacity: 1; pointer-events: auto; }
</style>
</head>
<body>
<header>
  <h1>promptdiff</h1>
  <small>Compare prompts &amp; measure similarity</small>
</header>
<main>
  <div class="inputs">
    <div class="panel">
      <label for="promptA">Prompt A (original)</label>
      <textarea id="promptA" placeholder="Paste your original prompt here…" spellcheck="false"></textarea>
    </div>
    <div class="panel">
      <label for="promptB">Prompt B (revised)</label>
      <textarea id="promptB" placeholder="Paste your revised prompt here…" spellcheck="false"></textarea>
    </div>
  </div>

  <div class="controls">
    <button class="btn-primary" onclick="runDiff('line')">Line diff</button>
    <button class="btn-secondary" onclick="runDiff('word')">Word diff</button>
    <button class="btn-outline" onclick="clearAll()">Clear</button>
    <button class="btn-outline" onclick="copyUnified()">Copy unified diff</button>
    <div id="similarity-badge">Similarity: —</div>
  </div>

  <div class="output-header">
    <h2>Diff</h2>
    <span id="mode-label"></span>
  </div>
  <div id="output"></div>
</main>
<div id="toast"></div>

<script>
  const promptA = () => document.getElementById('promptA').value;
  const promptB = () => document.getElementById('promptB').value;

  async function runDiff(mode) {
    const endpoint = mode === 'word' ? '/api/word-diff' : '/api/diff';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({a: promptA(), b: promptB()})
    });
    const data = await res.json();
    renderDiff(data.result, mode);

    const simRes = await fetch('/api/similarity', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({a: promptA(), b: promptB()})
    });
    const simData = await simRes.json();
    updateSimilarity(simData.score);

    document.getElementById('mode-label').textContent =
      mode === 'word' ? '(word-level)' : '(line-level)';
  }

  function renderDiff(result, mode) {
    const out = document.getElementById('output');
    out.innerHTML = '';
    if (mode === 'word') {
      result.forEach(([op, token], i) => {
        if (i > 0) out.appendChild(document.createTextNode(' '));
        const span = document.createElement('span');
        span.textContent = token;
        if (op === 'add')    span.className = 'w-add';
        if (op === 'remove') span.className = 'w-remove';
        out.appendChild(span);
      });
    } else {
      result.forEach(([op, line]) => {
        const span = document.createElement('span');
        const prefix = op === 'equal' ? ' ' : (op === 'add' ? '+' : '-');
        span.textContent = prefix + line;
        span.className = 'op-' + op;
        out.appendChild(span);
      });
    }
  }

  function updateSimilarity(score) {
    const badge = document.getElementById('similarity-badge');
    badge.textContent = 'Similarity: ' + score.toFixed(3);
    badge.className = score >= 0.75 ? 'high' : score >= 0.4 ? 'medium' : 'low';
  }

  async function copyUnified() {
    const res = await fetch('/api/unified', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({a: promptA(), b: promptB()})
    });
    const data = await res.json();
    await navigator.clipboard.writeText(data.unified);
    showToast('Unified diff copied to clipboard');
  }

  function clearAll() {
    document.getElementById('promptA').value = '';
    document.getElementById('promptB').value = '';
    document.getElementById('output').innerHTML = '';
    document.getElementById('mode-label').textContent = '';
    const badge = document.getElementById('similarity-badge');
    badge.textContent = 'Similarity: —';
    badge.className = '';
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  }

  // Keyboard shortcut: Ctrl+Enter / Cmd+Enter to run line diff
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runDiff('line');
  });
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/")
def index():
    return render_template_string(_TEMPLATE)


@app.route("/api/diff", methods=["POST"])
def api_diff():
    data = request.get_json(force=True)
    result = diff(data.get("a", ""), data.get("b", ""))
    return jsonify(result=result)


@app.route("/api/word-diff", methods=["POST"])
def api_word_diff():
    data = request.get_json(force=True)
    result = word_diff(data.get("a", ""), data.get("b", ""))
    return jsonify(result=result)


@app.route("/api/unified", methods=["POST"])
def api_unified():
    data = request.get_json(force=True)
    unified = format_unified(data.get("a", ""), data.get("b", ""))
    return jsonify(unified=unified)


@app.route("/api/similarity", methods=["POST"])
def api_similarity():
    data = request.get_json(force=True)
    score = similarity(data.get("a", ""), data.get("b", ""))
    return jsonify(score=score)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def launch(port: int = 5000, open_browser: bool = True) -> None:
    """Start the promptdiff web GUI.

    Parameters
    ----------
    port:
        TCP port for the development server. Defaults to ``5000``.
    open_browser:
        When *True* (default), open the interface in the default browser
        shortly after the server starts.
    """
    url = f"http://127.0.0.1:{port}"
    if open_browser:
        threading.Timer(0.8, webbrowser.open, args=[url]).start()
    print(f"promptdiff GUI running at {url}  (press Ctrl+C to quit)")
    app.run(port=port, debug=False)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``promptdiff-gui`` command."""
    parser = argparse.ArgumentParser(
        prog="promptdiff-gui",
        description="Launch the promptdiff web GUI.",
    )
    parser.add_argument(
        "--port", "-p", type=int, default=5000, help="port to listen on (default: 5000)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="do not open a browser window automatically",
    )
    args = parser.parse_args(argv)
    launch(port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
