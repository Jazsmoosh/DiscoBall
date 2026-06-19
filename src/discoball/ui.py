from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .config import Config
from .state import snapshot

_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>DiscoBall</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:24px;max-width:960px;background:#0b1020;color:#eef2ff}
    .card{border:1px solid #2b355f;background:#111936;border-radius:16px;padding:16px;margin-bottom:16px;box-shadow:0 8px 24px #0004}
    .row{display:flex;gap:16px;flex-wrap:wrap}
    .k{color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
    .v{font-size:16px;margin-top:4px;word-break:break-all}
    .bar{height:14px;background:#222b4d;border-radius:999px;overflow:hidden}
    .fill{height:100%;width:0%;background:linear-gradient(90deg,#22d3ee,#a855f7,#f472b6)}
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}
    h1{font-size:34px;margin-top:0}
  </style>
</head>
<body>
  <h1>🪩 DiscoBall</h1>
  <div class="card">
    <div class="row">
      <div style="flex:1;min-width:220px"><div class="k">Phase</div><div class="v" id="phase">-</div></div>
      <div style="flex:3;min-width:260px"><div class="k">Current</div><div class="v mono" id="current">-</div></div>
    </div>
    <div style="margin-top:14px">
      <div class="k">Stable wait progress</div>
      <div class="bar"><div class="fill" id="fill"></div></div>
      <div class="v" style="margin-top:6px" id="stable">-</div>
    </div>
    <div style="margin-top:10px"><div class="k">Detail</div><div class="v mono" id="detail">-</div></div>
  </div>

  <div class="card">
    <div class="row">
      <div style="flex:1;min-width:160px"><div class="k">Queued</div><div class="v" id="queued">0</div></div>
      <div style="flex:1;min-width:160px"><div class="k">Processed</div><div class="v" id="processed">0</div></div>
      <div style="flex:1;min-width:160px"><div class="k">Errors</div><div class="v" id="errors">0</div></div>
      <div style="flex:3;min-width:260px"><div class="k">Last done</div><div class="v mono" id="last">-</div></div>
    </div>
    <div style="margin-top:10px"><div class="k">Last error</div><div class="v mono" id="lerr">-</div></div>
  </div>
<script>
async function tick(){
  try {
    const r = await fetch('/api/status', {cache:'no-store'});
    const s = await r.json();
    document.getElementById('phase').textContent = s.phase || '-';
    document.getElementById('current').textContent = s.current_file || '-';
    document.getElementById('detail').textContent = s.detail || '-';
    document.getElementById('queued').textContent = s.queued ?? 0;
    document.getElementById('processed').textContent = s.processed ?? 0;
    document.getElementById('errors').textContent = s.errors ?? 0;
    document.getElementById('last').textContent = s.last_done || '-';
    document.getElementById('lerr').textContent = s.last_error || '-';
    const tgt = s.stable_target || 0;
    const el  = s.stable_elapsed || 0;
    const pct = (tgt>0) ? Math.min(100, Math.round((el/tgt)*100)) : 0;
    document.getElementById('fill').style.width = pct + '%';
    document.getElementById('stable').textContent = (tgt>0) ? `${el}s / ${tgt}s (${pct}%)` : '-';
  } catch(e) {}
}
tick(); setInterval(tick, 1000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # keep container logs clean
        return

    def do_GET(self):
        if self.path.startswith("/api/status"):
            body = json.dumps(snapshot()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path in {"/", ""} or self.path.startswith("/?"):
            body = _HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()


def start_ui(cfg: Config) -> None:
    if not cfg.ui_enabled:
        return

    def run() -> None:
        server = ThreadingHTTPServer(("0.0.0.0", cfg.ui_port), Handler)
        server.serve_forever()

    thread = threading.Thread(target=run, daemon=True, name="discoball-ui")
    thread.start()
