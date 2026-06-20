from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .config import Config
from .state import snapshot

_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="color-scheme" content="dark"/>
  <title>DiscoBall</title>
  <style>
    :root{
      --void:#050714;
      --night:#070b1d;
      --deep:#0c1230;
      --panel:rgba(14, 22, 52, .72);
      --panel-strong:rgba(18, 29, 71, .86);
      --stroke:rgba(198, 219, 255, .18);
      --stroke-strong:rgba(198, 219, 255, .28);
      --soft:rgba(255, 255, 255, .07);
      --text:#f3f7ff;
      --muted:#9fb0d2;
      --dim:#7180a3;
      --cyan:#65e7ff;
      --blue:#7ca7ff;
      --violet:#b26dff;
      --rose:#ff75d8;
      --gold:#ffe6a3;
      --green:#72f7bf;
      --red:#ff6f91;
      --shadow:0 22px 70px rgba(0,0,0,.42);
      --radius:24px;
    }

    *{box-sizing:border-box}
    html{min-height:100%}
    body{
      min-height:100vh;
      margin:0;
      color:var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background:
        radial-gradient(circle at 18% 16%, rgba(101,231,255,.22), transparent 24%),
        radial-gradient(circle at 78% 12%, rgba(255,117,216,.18), transparent 20%),
        radial-gradient(circle at 58% 86%, rgba(178,109,255,.19), transparent 24%),
        linear-gradient(180deg, var(--void), var(--night) 45%, #080b1a 100%);
      overflow-x:hidden;
    }

    body::before{
      content:"";
      position:fixed;
      inset:-20%;
      pointer-events:none;
      background:
        conic-gradient(from 120deg at 34% 46%, transparent 0 18%, rgba(101,231,255,.16) 24%, transparent 34%, rgba(255,117,216,.12) 44%, transparent 58%, rgba(255,230,163,.10) 72%, transparent 86%),
        radial-gradient(ellipse at 50% 50%, rgba(255,255,255,.08), transparent 35%);
      filter:blur(28px) saturate(1.25);
      opacity:.85;
      animation:dreamDrift 22s ease-in-out infinite alternate;
    }

    body::after{
      content:"";
      position:fixed;
      inset:0;
      pointer-events:none;
      background-image:
        radial-gradient(circle, rgba(255,255,255,.75) 0 1px, transparent 1.5px),
        radial-gradient(circle, rgba(101,231,255,.45) 0 1px, transparent 1.5px),
        radial-gradient(circle, rgba(255,117,216,.35) 0 1px, transparent 1.5px);
      background-size:190px 190px, 290px 290px, 410px 410px;
      background-position:24px 42px, 120px 160px, 260px 40px;
      opacity:.16;
      animation:starFloat 36s linear infinite;
    }

    @keyframes dreamDrift{
      from{transform:translate3d(-1.5%, -1%, 0) rotate(-2deg) scale(1)}
      to{transform:translate3d(1.5%, 1%, 0) rotate(2deg) scale(1.04)}
    }

    @keyframes starFloat{
      from{background-position:24px 42px, 120px 160px, 260px 40px}
      to{background-position:24px 232px, 120px 450px, 260px 450px}
    }

    .shell{
      position:relative;
      z-index:1;
      width:min(1220px, calc(100% - 32px));
      margin:0 auto;
      padding:34px 0 46px;
    }

    .hero{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:22px;
      margin-bottom:24px;
    }

    .brand{
      display:flex;
      align-items:center;
      gap:18px;
      min-width:0;
    }

    .orbWrap{
      width:74px;
      height:74px;
      display:grid;
      place-items:center;
      border-radius:28px;
      background:linear-gradient(145deg, rgba(255,255,255,.13), rgba(255,255,255,.03));
      border:1px solid var(--stroke);
      box-shadow:0 18px 54px rgba(101,231,255,.12), inset 0 0 30px rgba(255,255,255,.04);
      flex:0 0 auto;
    }

    .orb{
      width:54px;
      height:54px;
      border-radius:50%;
      position:relative;
      overflow:hidden;
      background:
        radial-gradient(circle at 32% 24%, rgba(255,255,255,.95), rgba(255,255,255,.18) 12%, transparent 24%),
        linear-gradient(135deg, var(--cyan) 0%, var(--blue) 30%, var(--violet) 62%, var(--rose) 100%);
      box-shadow:
        0 0 22px rgba(101,231,255,.42),
        0 0 38px rgba(255,117,216,.24),
        inset 0 -10px 24px rgba(0,0,0,.30),
        inset 0 0 0 1px rgba(255,255,255,.24);
      animation:orbBreathe 3.6s ease-in-out infinite;
    }

    .orb::before{
      content:"";
      position:absolute;
      inset:-4px;
      background:
        repeating-linear-gradient(90deg, rgba(255,255,255,.22) 0 1px, transparent 1px 8px),
        repeating-linear-gradient(0deg, rgba(255,255,255,.17) 0 1px, transparent 1px 8px);
      opacity:.72;
      mix-blend-mode:screen;
      transform:rotate(-7deg);
    }

    .orb::after{
      content:"";
      position:absolute;
      width:120%;
      height:35%;
      left:-10%;
      top:12%;
      background:linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent);
      transform:rotate(-25deg);
      animation:orbSweep 4.8s ease-in-out infinite;
    }

    @keyframes orbBreathe{
      0%,100%{filter:hue-rotate(0deg) saturate(1.15); transform:scale(1)}
      50%{filter:hue-rotate(18deg) saturate(1.35); transform:scale(1.045)}
    }

    @keyframes orbSweep{
      0%,22%{transform:translateX(-120%) rotate(-25deg); opacity:0}
      42%{opacity:.8}
      62%,100%{transform:translateX(120%) rotate(-25deg); opacity:0}
    }

    h1{
      margin:0;
      font-size:clamp(34px, 5vw, 58px);
      line-height:.95;
      letter-spacing:-.05em;
      font-weight:900;
      text-shadow:0 0 28px rgba(101,231,255,.18);
    }

    .tagline{
      margin:10px 0 0;
      color:var(--muted);
      font-size:14px;
      letter-spacing:.01em;
    }

    .statusPills{
      display:flex;
      justify-content:flex-end;
      align-items:center;
      gap:10px;
      flex-wrap:wrap;
    }

    .pill{
      display:inline-flex;
      align-items:center;
      gap:9px;
      min-height:40px;
      padding:10px 14px;
      border:1px solid var(--stroke);
      border-radius:999px;
      background:rgba(255,255,255,.055);
      color:var(--text);
      font-size:13px;
      backdrop-filter:blur(16px);
      box-shadow:inset 0 0 20px rgba(255,255,255,.03);
      white-space:nowrap;
    }

    .dot{
      width:9px;
      height:9px;
      border-radius:50%;
      background:var(--green);
      box-shadow:0 0 14px var(--green), 0 0 26px rgba(114,247,191,.35);
      animation:pulse 1.8s ease-in-out infinite;
    }
    .dot.idle{background:var(--dim); box-shadow:0 0 10px rgba(159,176,210,.18); animation:none}
    .dot.busy{background:var(--cyan); box-shadow:0 0 14px var(--cyan), 0 0 28px rgba(101,231,255,.35)}
    .dot.error{background:var(--red); box-shadow:0 0 14px var(--red), 0 0 28px rgba(255,111,145,.35)}

    @keyframes pulse{
      0%,100%{transform:scale(1); opacity:1}
      50%{transform:scale(1.35); opacity:.68}
    }

    .layout{
      display:grid;
      grid-template-columns:minmax(0, 1.45fr) minmax(340px, .9fr);
      gap:18px;
      align-items:start;
    }

    .panel{
      position:relative;
      border:1px solid var(--stroke);
      background:linear-gradient(180deg, var(--panel), rgba(7, 13, 32, .62));
      border-radius:var(--radius);
      box-shadow:var(--shadow), inset 0 1px 0 rgba(255,255,255,.06);
      overflow:hidden;
      backdrop-filter:blur(18px) saturate(1.15);
    }

    .panel::before{
      content:"";
      position:absolute;
      inset:0;
      pointer-events:none;
      background:linear-gradient(135deg, rgba(101,231,255,.12), transparent 34%, rgba(255,117,216,.08) 68%, transparent);
      opacity:.75;
    }

    .panel > *{position:relative; z-index:1}

    .panelHead{
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:16px;
      padding:20px 22px 10px;
    }

    .panelTitle{
      margin:0;
      font-size:15px;
      color:#dfe9ff;
      letter-spacing:.06em;
      text-transform:uppercase;
      font-weight:800;
    }

    .panelSub{
      margin:6px 0 0;
      color:var(--muted);
      font-size:12px;
      line-height:1.45;
    }

    .panelBody{padding:10px 22px 22px}

    .phaseRow{
      display:flex;
      align-items:center;
      gap:12px;
      flex-wrap:wrap;
      margin-bottom:16px;
    }

    .phaseChip{
      display:inline-flex;
      align-items:center;
      gap:10px;
      border:1px solid var(--stroke-strong);
      border-radius:999px;
      padding:11px 15px;
      background:linear-gradient(135deg, rgba(101,231,255,.12), rgba(178,109,255,.14), rgba(255,117,216,.09));
      font-weight:850;
      text-transform:capitalize;
      letter-spacing:.01em;
      box-shadow:0 0 28px rgba(101,231,255,.10), inset 0 0 20px rgba(255,255,255,.03);
    }

    .ghostText{color:var(--muted); font-size:13px}

    .fileBox{
      border:1px solid rgba(198,219,255,.13);
      background:rgba(255,255,255,.045);
      border-radius:20px;
      padding:17px;
      margin-bottom:16px;
    }

    .label{
      margin-bottom:8px;
      color:var(--muted);
      font-size:11px;
      font-weight:800;
      letter-spacing:.13em;
      text-transform:uppercase;
    }

    .mono{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace}
    .currentFile{min-height:24px; word-break:break-word; color:#f8fbff; font-size:15px}
    .detailText{margin-top:12px; color:#dce7ff; font-size:14px; line-height:1.5}

    .progressArea{margin-top:18px}
    .progressMeta{display:flex; justify-content:space-between; gap:12px; color:var(--muted); font-size:13px; margin-bottom:10px}
    .bar{
      height:15px;
      border-radius:999px;
      overflow:hidden;
      background:rgba(255,255,255,.07);
      border:1px solid rgba(255,255,255,.08);
      box-shadow:inset 0 1px 8px rgba(0,0,0,.35);
    }
    .fill{
      width:0%;
      height:100%;
      border-radius:inherit;
      position:relative;
      background:linear-gradient(90deg, var(--cyan), var(--blue) 38%, var(--violet) 68%, var(--rose));
      box-shadow:0 0 18px rgba(101,231,255,.25), inset 0 0 12px rgba(255,255,255,.16);
      transition:width .45s ease;
      overflow:hidden;
    }
    .fill::after{
      content:"";
      position:absolute;
      inset:0;
      background:linear-gradient(90deg, transparent, rgba(255,255,255,.35), transparent);
      transform:translateX(-120%);
      animation:shimmer 2.4s ease-in-out infinite;
    }
    @keyframes shimmer{to{transform:translateX(120%)}}

    .statsGrid{display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:14px}
    .stat{
      min-height:112px;
      padding:16px;
      border:1px solid rgba(198,219,255,.12);
      border-radius:20px;
      background:rgba(255,255,255,.045);
      box-shadow:inset 0 1px 0 rgba(255,255,255,.035);
    }
    .statKey{color:var(--muted); font-size:11px; font-weight:850; letter-spacing:.13em; text-transform:uppercase; margin-bottom:10px}
    .statVal{font-size:34px; line-height:1; font-weight:950; letter-spacing:-.04em}
    .statVal.good{color:var(--green); text-shadow:0 0 22px rgba(114,247,191,.16)}
    .statVal.bad{color:var(--red); text-shadow:0 0 22px rgba(255,111,145,.16)}
    .statSub{margin-top:10px; color:var(--muted); font-size:12px; line-height:1.4; word-break:break-word}

    .wide{grid-column:1 / -1}
    .bottomGrid{display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:18px; margin-top:18px}
    .miniBody{padding:0 22px 22px; color:#dce7ff; line-height:1.5; font-size:14px; word-break:break-word}
    .callout{
      border-left:3px solid var(--cyan);
      padding:12px 14px;
      border-radius:14px;
      background:rgba(101,231,255,.07);
      color:#e9f5ff;
    }

    .footer{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:14px;
      flex-wrap:wrap;
      margin-top:18px;
      color:var(--muted);
      font-size:12px;
      padding:0 4px;
    }

    @media (max-width:980px){
      .hero{align-items:flex-start; flex-direction:column}
      .statusPills{justify-content:flex-start}
      .layout{grid-template-columns:1fr}
      .bottomGrid{grid-template-columns:1fr}
    }
    @media (max-width:640px){
      .shell{width:min(100% - 20px, 1220px); padding:22px 0 34px}
      .orbWrap{width:62px; height:62px; border-radius:22px}
      .orb{width:46px; height:46px}
      .statsGrid{grid-template-columns:1fr}
      .panelHead,.panelBody,.miniBody{padding-left:16px; padding-right:16px}
    }
    @media (prefers-reduced-motion: reduce){
      *,*::before,*::after{animation-duration:.001ms!important; animation-iteration-count:1!important; transition:none!important}
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div class="brand">
        <div class="orbWrap"><div class="orb" aria-hidden="true"></div></div>
        <div>
          <h1>DiscoBall</h1>
          <p class="tagline">MakeMKV post-process monitor Â· identify Â· rename Â· organize</p>
        </div>
      </div>
      <div class="statusPills">
        <div class="pill"><span class="dot idle" id="liveDot"></span><strong id="liveLabel">Idle</strong></div>
        <div class="pill">Updated <strong id="updatedAt">never</strong></div>
      </div>
    </header>

    <section class="layout">
      <article class="panel">
        <div class="panelHead">
          <div>
            <h2 class="panelTitle">Current Activity</h2>
            <p class="panelSub">Live status for the watcher, stability window, and active file operation.</p>
          </div>
        </div>
        <div class="panelBody">
          <div class="phaseRow">
            <div class="phaseChip" id="phaseChip">Idle</div>
            <div class="ghostText" id="phaseHint">Waiting for media.</div>
          </div>

          <div class="fileBox">
            <div class="label">Current file</div>
            <div class="currentFile mono" id="currentFile">-</div>
            <div class="detailText" id="detailText">Standing by for a completed MakeMKV output file.</div>

            <div class="progressArea">
              <div class="progressMeta"><span>Stable wait progress</span><span id="stableText">Awaiting file</span></div>
              <div class="bar"><div class="fill" id="progressFill"></div></div>
            </div>
          </div>
        </div>
      </article>

      <aside class="panel">
        <div class="panelHead">
          <div>
            <h2 class="panelTitle">Run Summary</h2>
            <p class="panelSub">Processing totals since this container started.</p>
          </div>
        </div>
        <div class="panelBody">
          <div class="statsGrid">
            <div class="stat"><div class="statKey">Queued</div><div class="statVal" id="queuedVal">0</div><div class="statSub">Files waiting for worker pickup.</div></div>
            <div class="stat"><div class="statKey">Processed</div><div class="statVal good" id="processedVal">0</div><div class="statSub">Files successfully organized.</div></div>
            <div class="stat"><div class="statKey">Errors</div><div class="statVal bad" id="errorsVal">0</div><div class="statSub">Items requiring attention.</div></div>
            <div class="stat"><div class="statKey">Last done</div><div class="statVal" style="font-size:18px;line-height:1.2" id="lastDoneVal">-</div><div class="statSub mono" id="lastDoneWhen">No completed files yet.</div></div>
          </div>
        </div>
      </aside>
    </section>

    <section class="bottomGrid">
      <article class="panel">
        <div class="panelHead"><div><h2 class="panelTitle">Watcher</h2><p class="panelSub">Container path being monitored.</p></div></div>
        <div class="miniBody"><div class="label">Path</div><div class="mono" id="watchPath">/watch</div></div>
      </article>
      <article class="panel">
        <div class="panelHead"><div><h2 class="panelTitle">Last Error</h2><p class="panelSub">Most recent processing issue.</p></div></div>
        <div class="miniBody"><div class="mono" id="lastErrorVal">-</div></div>
      </article>
      <article class="panel">
        <div class="panelHead"><div><h2 class="panelTitle">Operating Note</h2><p class="panelSub">Safe behavior reminder.</p></div></div>
        <div class="miniBody"><div class="callout">DiscoBall waits for the file size to stop changing before metadata lookup and move/rename.</div></div>
      </article>
    </section>

    <footer class="footer">
      <span>Cyberdream UI Â· no external assets Â· no telemetry</span>
      <span>Polling <code>/api/status</code> every second</span>
    </footer>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);

    function text(value, fallback='-'){
      if(value === null || value === undefined || value === '') return fallback;
      return String(value);
    }

    function since(epoch){
      if(!epoch) return 'never';
      const diff = Math.max(0, Math.floor(Date.now()/1000 - Number(epoch)));
      if(diff < 5) return 'just now';
      if(diff < 60) return diff + 's ago';
      if(diff < 3600) return Math.floor(diff/60) + 'm ago';
      if(diff < 86400) return Math.floor(diff/3600) + 'h ago';
      return Math.floor(diff/86400) + 'd ago';
    }

    function toneFor(phase, errors){
      const p = String(phase || '').toLowerCase();
      if(p.includes('error') || p.includes('fail')) return 'error';
      if(errors > 0 && (p === 'idle' || p === 'watching')) return 'error';
      if(p === 'idle') return 'idle';
      return 'busy';
    }

    function humanPhase(phase){
      const p = text(phase, 'idle');
      return p.charAt(0).toUpperCase() + p.slice(1).replaceAll('_',' ');
    }

    function phaseHint(phase){
      const p = String(phase || '').toLowerCase();
      if(p.includes('stable')) return 'Waiting for MakeMKV to finish writing.';
      if(p.includes('process') || p.includes('identify') || p.includes('move')) return 'Metadata and file organization are running.';
      if(p.includes('watch')) return 'Watching the MakeMKV output folder.';
      if(p.includes('error') || p.includes('fail')) return 'Review the last error panel and container logs.';
      return 'Waiting for media.';
    }

    async function tick(){
      try{
        const response = await fetch('/api/status', {cache:'no-store'});
        if(!response.ok) throw new Error('HTTP ' + response.status);
        const s = await response.json();

        const phase = text(s.phase, 'idle');
        const errors = Number(s.errors || 0);
        const stableTarget = Number(s.stable_target || 0);
        const stableElapsed = Number(s.stable_elapsed || 0);
        const pct = stableTarget > 0 ? Math.min(100, Math.round((stableElapsed / stableTarget) * 100)) : 0;
        const tone = toneFor(phase, errors);

        $('phaseChip').textContent = humanPhase(phase);
        $('phaseHint').textContent = phaseHint(phase);
        $('liveLabel').textContent = tone === 'error' ? 'Attention' : humanPhase(phase);
        $('liveDot').className = 'dot ' + tone;
        $('updatedAt').textContent = since(s.updated_at);

        $('currentFile').textContent = text(s.current_file, '-');
        $('detailText').textContent = text(s.detail, 'Standing by for a completed MakeMKV output file.');
        $('queuedVal').textContent = Number(s.queued || 0);
        $('processedVal').textContent = Number(s.processed || 0);
        $('errorsVal').textContent = errors;
        $('lastDoneVal').textContent = text(s.last_done, '-');
        $('lastDoneWhen').textContent = s.last_done_at ? since(s.last_done_at) : 'No completed files yet.';
        $('lastErrorVal').textContent = text(s.last_error, '-');

        $('progressFill').style.width = pct + '%';
        $('stableText').textContent = stableTarget > 0 ? `${stableElapsed}s / ${stableTarget}s (${pct}%)` : 'Awaiting file';
      } catch(err){
        $('liveDot').className = 'dot error';
        $('liveLabel').textContent = 'Offline';
        $('updatedAt').textContent = 'unreachable';
        $('lastErrorVal').textContent = 'Could not reach /api/status';
      }
    }

    tick();
    setInterval(tick, 1000);
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/status"):
            self._send_json(snapshot())
            return
        if self.path.startswith("/api/health") or self.path.startswith("/healthz"):
            self._send_json({"ok": True, "service": "discoball"})
            return
        if self.path in {"/", ""} or self.path.startswith("/?"):
            self._send_html(_HTML)
            return
        self.send_response(404)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()


def start_ui(cfg: Config) -> None:
    if not cfg.ui_enabled:
        return

    def run() -> None:
        server = ThreadingHTTPServer(("0.0.0.0", cfg.ui_port), Handler)
        server.serve_forever()

    thread = threading.Thread(target=run, daemon=True, name="discoball-ui")
    thread.start()

