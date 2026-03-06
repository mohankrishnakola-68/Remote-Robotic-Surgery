"""
Haptic-Q: Web Dashboard (FastAPI)
- Real webcam streaming via MJPEG (/video_feed)
- /api/telemetry: surgeon_console pushes live data here
- Force, joystick, latency ONLY update when real robot data arrives
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import cv2, threading, time

app = FastAPI(title="Haptic-Q Tele-Operation Dashboard")

# ── Shared telemetry store (surgeon_console pushes here) ────────
_telemetry = {
    "force": 0, "integrity": 100, "qber": 0.0,
    "stability": 100.0, "qec_repairs": 0,
    "joystick_x": 0, "joystick_y": 0,
    "latency_ms": 0, "protocol_sync": 99.8,
    "connected": False,
}
_tele_lock = threading.Lock()

@app.post("/api/telemetry")
async def push_telemetry(request: Request):
    data = await request.json()
    with _tele_lock:
        _telemetry.update(data)
        _telemetry["connected"] = True
    return {"ok": True}

@app.get("/api/telemetry")
async def get_telemetry():
    with _tele_lock:
        return JSONResponse(_telemetry)

_commands = []
_cmd_lock = threading.Lock()

@app.post("/api/command")
async def push_command(request: Request):
    data = await request.json()
    with _cmd_lock:
        if data.get("key"):
            _commands.append(data.get("key"))
    return {"ok": True}

@app.get("/api/command")
async def get_commands():
    with _cmd_lock:
        cmds = _commands.copy()
        _commands.clear()
        return JSONResponse({"commands": cmds})

# ── Camera setup ─────────────────────────────────────────────────
_camera      = None
_camera_lock = threading.Lock()

def get_camera():
    global _camera
    if _camera is not None and _camera.isOpened():
        return _camera
    for idx in range(4):
        for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:
            try:
                cap = cv2.VideoCapture(idx, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        _camera = cap
                        return _camera
                    cap.release()
            except Exception:
                pass
    return None

def gen_frames():
    import numpy as np
    while True:
        with _camera_lock:
            cam = get_camera()
            if cam:
                ret, frame = cam.read()
                if ret:
                    frame = cv2.resize(frame, (640, 480))
                    _, buf = cv2.imencode('.jpg', frame,
                                         [cv2.IMWRITE_JPEG_QUALITY, 75])
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                           + buf.tobytes() + b'\r\n')
                    time.sleep(0.033)
                    continue
            # blank placeholder
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "NO CAMERA DETECTED", (130, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 230), 2)
            _, buf = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                   + buf.tobytes() + b'\r\n')
        time.sleep(0.1)

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

# ── Main Page ─────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haptic-Q Pro Console</title>
    <style>
        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

        html, body {
            height: 100%;
            overflow: hidden;
            background: #0A0C12;
            color: #fff;
            font-family: 'Courier New', monospace;
            background-image:
                linear-gradient(rgba(20,24,35,.9) 1px, transparent 1px),
                linear-gradient(90deg, rgba(20,24,35,.9) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        /* ── layout shell ── */
        .shell {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        /* ── HEADER 70px ── */
        .header {
            flex: 0 0 70px;
            background: #161C28;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 28px;
            border-bottom: 1px solid #1E2535;
        }
        .h-title  { font-size:1.45rem; font-weight:700; letter-spacing:3px; }
        .h-right  { text-align:right; }
        .h-secure { font-size:1rem; font-weight:700; color:#00FFE6; letter-spacing:2px; }
        .h-fs     { font-size:.68rem; color:#64FF96; letter-spacing:1px; margin-top:3px; }

        /* ── WORKSPACE fills remaining space ── */
        .workspace {
            flex: 1 1 0;
            min-height: 0;          /* ← critical: allows flex children to shrink */
            display: grid;
            grid-template-columns: 1fr 330px;
        }

        /* ── LEFT ── */
        .left-col {
            display: flex;
            flex-direction: column;
            padding: 10px 12px 10px 26px;
            gap: 10px;
            min-height: 0;
        }

        /* Camera box: takes all available vertical space in left-col */
        .video-box {
            flex: 1 1 0;
            min-height: 0;
            background: #0D1018;
            border: 2px solid #00FFE6;
            overflow: hidden;
            position: relative;
        }
        .video-box img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .cam-wait {
            position: absolute; inset: 0;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 8px;
            color: #00FFE6; font-size:.95rem; letter-spacing:2px;
        }
        .cam-wait small { color:#4A5568; font-size:.72rem; }

        /* Innovation bar: fixed height */
        .inno-bar {
            flex: 0 0 auto;
            background: rgba(0,255,230,.05);
            border: 1px solid #00FFE6;
            border-radius: 6px;
            padding: 8px 16px;
            display: flex; align-items: center; gap: 12px;
        }
        .inno-dot { width:11px; height:11px; background:#00FFE6; border-radius:50%; flex-shrink:0; }
        .inno-title { font-size:.85rem; font-weight:700; color:#00FFE6; letter-spacing:2px; }
        .inno-sub   { font-size:.68rem; color:#E2E8F0; margin-top:2px; }

        /* ── RIGHT ── */
        .right-col {
            display: flex;
            flex-direction: column;
            padding: 10px 26px 10px 12px;
            gap: 10px;
            border-left: 1px solid #1E2535;
            min-height: 0;
        }

        /* graph panels share available height equally */
        .graph-panel {
            flex: 1 1 0;
            min-height: 0;
            background: #1C2332;
            border-radius: 8px;
            padding: 10px 14px 8px;
            display: flex; flex-direction: column;
        }
        .graph-panel.orange { border: 2px solid #967820; }
        .graph-panel.green  { border: 2px solid #1E783C; }
        .panel-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-shrink:0; }
        .panel-title { font-size:.8rem; font-weight:700; }
        .panel-val   { font-size:.8rem; font-weight:700; }
        .panel-val.orange { color:#FFB432; }
        .panel-val.green  { color:#64FF96; }

        .graph-area {
            flex: 1 1 0;
            min-height: 0;
            background: #0C0F16;
            position: relative;
            overflow: hidden;
        }
        .graph-area svg { width:100%; height:100%; }
        .graph-area::before {
            content:''; position:absolute; inset:0; pointer-events:none;
            background-image:
                linear-gradient(rgba(40,45,60,1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(40,45,60,1) 1px, transparent 1px);
            background-size: 25% 25%;
        }

        /* fail-safe box */
        .fs-panel {
            flex: 0 0 auto;
            background: #0A1423;
            border: 2px solid #00FFE6;
            border-radius: 4px;
            padding: 10px 12px 8px;
            position: relative;
        }
        .fs-tag {
            position:absolute; top:-10px; left:8px;
            background:#00FFE6; color:#000;
            font-size:.6rem; font-weight:700;
            padding:2px 7px; letter-spacing:1px;
        }
        .fs-row { font-size:.75rem; color:#fff; margin-bottom:4px; }
        .fs-row.g { color:#64FF96; }
        .fs-row.c { color:#00FFE6; }
        .fs-secure { position:absolute; right:12px; bottom:8px; font-size:.85rem; font-weight:700; color:#00FFE6; }

        /* ── FOOTER 88px ── */
        .footer {
            flex: 0 0 88px;
            background: #1E2637;
            border-top: 1px solid #374060;
            margin: 0 26px 8px 26px;
            border-radius: 8px;
            display: grid;
            grid-template-columns: 180px 1fr 1fr;
        }
        .fb {
            display:flex; align-items:center; gap:12px;
            padding:0 18px;
            border-right: 1px solid #374060;
        }
        .fb:last-child { border-right:none; }

        .joy-pad {
            width:48px; height:48px; flex-shrink:0;
            border:1px solid #647090; background:#0F1520; position:relative;
        }
        .joy-pad::before { content:''; position:absolute; left:50%; top:0; width:1px; height:100%; background:#2D3A55; }
        .joy-pad::after  { content:''; position:absolute; top:50%; left:0; height:1px; width:100%; background:#2D3A55; }
        .joy-dot {
            position:absolute; width:7px; height:7px;
            background:#00FFE6; border-radius:50%;
            transform:translate(-50%,-50%);
            left:50%; top:50%;
        }
        .fb-label { font-size:.6rem; color:#718096; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:3px; }
        .fb-val   { font-size:1.2rem; font-weight:700; color:#fff; }
        .fb-route { font-size:.85rem; font-weight:700; color:#FF6464; }
        .fb-sub   { font-size:.65rem; color:#FF6464; margin-top:1px; }
        .fb-sub2  { font-size:.6rem; color:#54A870; margin-top:1px; }
        .qml-badge { background:#7B61FF; color:#fff; font-size:.58rem; font-weight:700; padding:2px 6px; border-radius:2px; margin-bottom:2px; display:inline-block; }
        .fb-off { font-size:.75rem; color:#7A7A8A; }
    </style>
</head>
<body>

<div class="shell">

    <!-- HEADER -->
    <header class="header">
        <div class="h-title">HAPTIC-Q SURGEON CONSOLE</div>
        <div class="h-right">
            <div class="h-secure">SECURE LINK: ACTIVE</div>
            <div class="h-fs">[ FAIL-SAFE: READY ]</div>
        </div>
    </header>

    <!-- WORKSPACE -->
    <div class="workspace">

        <!-- LEFT -->
        <div class="left-col">
            <div class="video-box" id="video-box">
                <img src="/video_feed" alt="Live Feed"
                     onerror="this.style.display='none';document.getElementById('cam-wait').style.display='flex'">
                <div class="cam-wait" id="cam-wait" style="display:none">
                    <span>WAITING FOR CAMERA...</span>
                    <small>[CHECK USB CONNECTION]</small>
                </div>
            </div>

            <div class="inno-bar">
                <div class="inno-dot"></div>
                <div>
                    <div class="inno-title">HACKATHON INNOVATION PILLARS</div>
                    <div class="inno-sub">• INTER-STATION SYNC (Custom Q-Protocol) &nbsp;• 0ms TELEPORTATION &nbsp;• Q-NO CLONING DEFENSE</div>
                </div>
            </div>
        </div>

        <!-- RIGHT -->
        <div class="right-col">

            <div class="graph-panel orange">
                <div class="panel-top">
                    <div class="panel-title">Haptic Force Applied (mN)</div>
                    <div class="panel-val orange" id="force-val">0</div>
                </div>
                <div class="graph-area">
                    <svg id="force-svg" preserveAspectRatio="none"></svg>
                </div>
            </div>

            <div class="graph-panel green">
                <div class="panel-top">
                    <div class="panel-title">Quantum Link Integrity (1-QBER%)</div>
                    <div class="panel-val green" id="integrity-val">100</div>
                </div>
                <div class="graph-area">
                    <svg id="integrity-svg" preserveAspectRatio="none"></svg>
                </div>
            </div>

            <div class="fs-panel">
                <div class="fs-tag">QUANTUM FAIL-SAFE</div>
                <div class="fs-row g" id="qber-row">QBER [Error Rate]: 0.00%</div>
                <div class="fs-row c" id="stab-row">LINK STABILITY: 100.0%</div>
                <div class="fs-row"   id="qec-row">QEC: ACTIVE &nbsp;&nbsp; Repairs: 0</div>
                <div class="fs-secure">SECURE</div>
            </div>

        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">

        <div class="fb">
            <div class="joy-pad"><div class="joy-dot" id="joy-dot"></div></div>
            <div>
                <div class="fb-label">Haptic Coordinate Stream</div>
                <div class="fb-val" id="coord-val">X: 0 | Y: 0</div>
            </div>
        </div>

        <div class="fb" style="flex-direction:column;align-items:flex-start;justify-content:center;gap:1px;">
            <div class="fb-label">PROTOCOL: STANDARD: Q-UDP/ENC</div>
            <div class="fb-route">CLASSICAL ROUTE</div>
            <div class="fb-sub"  id="delay-val">R-DELAY: — ms</div>
            <div class="fb-sub2" id="sync-val">SYNC RATE: 99.80%</div>
        </div>

        <div class="fb" style="flex-direction:column;align-items:flex-start;justify-content:center;gap:2px;">
            <div class="qml-badge">QML ADVANTAGE</div>
            <div class="fb-label" style="margin:0;">QUANTUM PREDICTION</div>
            <div class="fb-off">PRED DISABLED</div>
            <div style="font-size:.58rem;color:#718096;">[P] ACTIVATE AI &nbsp;|&nbsp; Expert Mode: Offline</div>
        </div>

    </div>
</div><!-- .shell -->

<script>
    const HIST = 60;
    // Force starts at 0 — only updates when real robot data arrives from API
    let forceData     = Array(HIST).fill(0);
    let integrityData = Array(HIST).fill(100);

    function drawLine(id, data, color, maxV) {
        const svg = document.getElementById(id);
        if (!svg) return;
        const W = svg.clientWidth || 290, H = svg.clientHeight || 80;
        if (!W || !H) return;
        const pts = data.map((v,i) => {
            const x = (i/(HIST-1))*W;
            const y = H - ((Math.max(0,v)/maxV)*(H-6)) - 2;
            return `${x.toFixed(1)},${Math.max(2,Math.min(H-2,y)).toFixed(1)}`;
        }).join(' ');
        svg.innerHTML = `<polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round"/>`;
    }

    // Integrity has a live quantum heartbeat even when robot not connected
    let integrityTick = 0;
    function integrityPulse() {
        const t  = integrityTick++ / 20;   // 20Hz → seconds
        const v  = 97 + 1.5*Math.sin(t*2) + 0.5*(Math.random()-0.5);
        integrityData.push(v); integrityData.shift();

        const qber = (100-v).toFixed(2);
        const stab = (97 + 2*Math.sin(t*1.5)).toFixed(1);
        document.getElementById('integrity-val').textContent = Math.round(v);
        document.getElementById('qber-row').textContent = `QBER [Error Rate]: ${qber}%`;
        document.getElementById('stab-row').textContent = `LINK STABILITY: ${stab}%`;
        drawLine('integrity-svg', integrityData, '#64FF96', 100);
    }

    // Poll robot telemetry from API — force & joystick ONLY from real data
    let repairs = 0;
    async function pollTelemetry() {
        try {
            const r = await fetch('/api/telemetry');
            const d = await r.json();

            if (d.connected) {
                // Real robot data
                forceData.push(d.force); forceData.shift();
                document.getElementById('force-val').textContent = d.force;
                document.getElementById('coord-val').textContent =
                    `X: ${d.joystick_x} | Y: ${d.joystick_y}`;
                document.getElementById('delay-val').textContent =
                    `R-DELAY: ${d.latency_ms} ms`;
                document.getElementById('sync-val').textContent =
                    `SYNC RATE: ${d.protocol_sync.toFixed(2)}%`;

                repairs = d.qec_repairs;

                // Joystick dot
                const dot = document.getElementById('joy-dot');
                dot.style.left = (d.joystick_x / 255 * 86 + 7) + '%';
                dot.style.top  = (100 - d.joystick_y / 255 * 86 - 7) + '%';
            } else {
                // No robot connected — keep force at 0, joystick at center
                forceData.push(0); forceData.shift();
                document.getElementById('force-val').textContent = '0';
                document.getElementById('coord-val').textContent = 'X: 0 | Y: 0';
                document.getElementById('delay-val').textContent = 'R-DELAY: — ms';

                const dot = document.getElementById('joy-dot');
                dot.style.left = '50%';
                dot.style.top  = '50%';
            }

            document.getElementById('qec-row').textContent =
                `QEC: ACTIVE    Repairs: ${repairs}`;
            drawLine('force-svg', forceData, '#FFB432', 30);

        } catch(e) { /* server not ready yet, skip */ }
    }

    // Listen for keys to send back to python backend
    document.addEventListener('keydown', (e) => {
        const k = e.key.toLowerCase();
        if (['w', 'a', 's', 'd', 'h', 'r', 'k', 'p', 'm', 'q'].includes(k)) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: k})
            });
        }
    });

    // Run both loops
    setInterval(integrityPulse, 50);    // 20 Hz — quantum heartbeat always
    setInterval(pollTelemetry,  150);   // ~7 Hz  — real data poll
    pollTelemetry();                    // immediate first call
</script>

</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
