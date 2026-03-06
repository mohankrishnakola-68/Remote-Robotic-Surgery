from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import random, time

app = FastAPI(title="Haptic-Q Tele-Operation Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haptic-Q Pro Console</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background-color: #0A0C12;
            color: #FFFFFF;
            font-family: 'Courier New', Courier, monospace;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background-image:
                linear-gradient(rgba(20,24,35,0.8) 1px, transparent 1px),
                linear-gradient(90deg, rgba(20,24,35,0.8) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        /* ── HEADER ── */
        .header {
            height: 80px;
            background: #161C28;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 30px;
            border-bottom: 1px solid #1E2535;
            flex-shrink: 0;
        }
        .header-title {
            font-size: 1.6rem;
            font-weight: bold;
            letter-spacing: 3px;
            color: #FFFFFF;
        }
        .header-status { text-align: right; }
        .status-secure {
            font-size: 1.1rem;
            font-weight: bold;
            color: #00FFE6;
            letter-spacing: 2px;
        }
        .status-failsafe {
            font-size: 0.7rem;
            color: #64FF96;
            letter-spacing: 1px;
            margin-top: 4px;
        }

        /* ── MAIN WORKSPACE ── */
        .workspace {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 0;
            min-height: 0;
        }

        /* ── LEFT SIDE ── */
        .left-col {
            display: flex;
            flex-direction: column;
            padding: 15px 15px 10px 30px;
            gap: 12px;
        }

        .video-box {
            flex: 1;
            background: #0D1018;
            border: 2px solid #00FFE6;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #00FFE6;
            font-size: 1rem;
            letter-spacing: 2px;
        }
        .video-waiting { text-align: center; }
        .video-waiting div:first-child { font-size: 1.1rem; margin-bottom: 8px; }
        .video-waiting div:last-child { font-size: 0.75rem; color: #4A5568; }

        .innovation-bar {
            background: rgba(0,255,230,0.05);
            border: 1px solid #00FFE6;
            border-radius: 6px;
            padding: 10px 18px;
            display: flex;
            align-items: center;
            gap: 14px;
            flex-shrink: 0;
        }
        .inno-dot {
            width: 12px; height: 12px;
            background: #00FFE6;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .inno-title {
            font-size: 0.9rem;
            font-weight: bold;
            color: #00FFE6;
            letter-spacing: 2px;
        }
        .inno-sub {
            font-size: 0.72rem;
            color: #E2E8F0;
            margin-top: 3px;
            letter-spacing: 0.5px;
        }

        /* ── RIGHT SIDE ── */
        .right-col {
            display: flex;
            flex-direction: column;
            padding: 15px 30px 10px 15px;
            gap: 12px;
            border-left: 1px solid #1E2535;
        }

        /* Graph Panels */
        .graph-panel {
            background: #1C2332;
            border-radius: 8px;
            padding: 14px 16px 10px;
            position: relative;
        }
        .graph-panel.orange { border: 2px solid #967820; }
        .graph-panel.green  { border: 2px solid #1E783C; }

        .panel-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .panel-title { font-size: 0.85rem; font-weight: bold; color: #FFFFFF; }
        .panel-val { font-size: 0.85rem; font-weight: bold; }
        .panel-val.orange { color: #FFB432; }
        .panel-val.green  { color: #64FF96; }

        /* Graph SVG line chart area */
        .graph-area {
            background: #0C0F16;
            height: 90px;
            position: relative;
            overflow: hidden;
        }
        .graph-area svg { width: 100%; height: 100%; }

        /* Grid on graph */
        .graph-area::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(40,45,60,1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(40,45,60,1) 1px, transparent 1px);
            background-size: 25% 25%;
            pointer-events: none;
        }

        /* Fail-safe box */
        .failsafe-panel {
            background: #0A1423;
            border: 2px solid #00FFE6;
            border-radius: 4px;
            padding: 12px 14px 10px;
            position: relative;
            flex-shrink: 0;
        }
        .failsafe-tag {
            position: absolute;
            top: -11px; left: 8px;
            background: #00FFE6;
            color: #000;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 8px;
            letter-spacing: 1px;
        }
        .fs-row {
            font-size: 0.78rem;
            color: #FFFFFF;
            margin-bottom: 5px;
        }
        .fs-row.green  { color: #64FF96; }
        .fs-row.cyan   { color: #00FFE6; }
        .secure-badge {
            position: absolute;
            right: 14px; bottom: 10px;
            font-size: 0.9rem;
            font-weight: bold;
            color: #00FFE6;
        }

        /* ── FOOTER ── */
        .footer-bar {
            height: 95px;
            background: #1E2637;
            border: 1px solid #647090;
            border-radius: 8px;
            margin: 0 30px 12px 30px;
            display: grid;
            grid-template-columns: 200px 1fr 1fr;
            flex-shrink: 0;
        }
        .footer-block {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 0 20px;
            border-right: 1px solid #374060;
        }
        .footer-block:last-child { border-right: none; }

        .joystick-pad {
            width: 52px; height: 52px;
            border: 1px solid #647090;
            background: #0F1520;
            position: relative;
            flex-shrink: 0;
        }
        .joystick-pad::before {
            content: '';
            position: absolute;
            left: 50%; top: 0; width: 1px; height: 100%;
            background: #2D3A55;
        }
        .joystick-pad::after {
            content: '';
            position: absolute;
            top: 50%; left: 0; height: 1px; width: 100%;
            background: #2D3A55;
        }
        .joy-dot {
            position: absolute;
            width: 8px; height: 8px;
            background: #00FFE6;
            border-radius: 50%;
            transform: translate(-50%, -50%);
        }

        .footer-text { display: flex; flex-direction: column; }
        .ft-label {
            font-size: 0.65rem;
            color: #718096;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .ft-val {
            font-size: 1.3rem;
            font-weight: bold;
            color: #FFFFFF;
            letter-spacing: 1px;
        }
        .ft-route {
            font-size: 0.95rem;
            font-weight: bold;
            color: #FF6464;
        }
        .ft-sub { font-size: 0.7rem; color: #FF6464; margin-top: 2px; }
        .ft-sub2 { font-size: 0.65rem; color: #54A870; margin-top: 2px; }

        .qml-badge {
            background: #7B61FF;
            color: #FFF;
            font-size: 0.6rem;
            font-weight: bold;
            padding: 2px 7px;
            border-radius: 2px;
            margin-bottom: 3px;
            display: inline-block;
        }
        .ft-disabled { font-size: 0.8rem; color: #7A7A8A; }
    </style>
</head>
<body>

    <!-- HEADER -->
    <header class="header">
        <div class="header-title">HAPTIC-Q SURGEON CONSOLE</div>
        <div class="header-status">
            <div class="status-secure" id="link-status">SECURE LINK: ACTIVE</div>
            <div class="status-failsafe">[ FAIL-SAFE: READY ]</div>
        </div>
    </header>

    <!-- MAIN WORKSPACE -->
    <div class="workspace">

        <!-- LEFT COLUMN -->
        <div class="left-col">
            <div class="video-box">
                <div class="video-waiting">
                    <div>WAITING FOR CAMERA...</div>
                    <div>[CHECK USB CONNECTION]</div>
                </div>
            </div>

            <div class="innovation-bar">
                <div class="inno-dot"></div>
                <div>
                    <div class="inno-title">HACKATHON INNOVATION PILLARS</div>
                    <div class="inno-sub">• INTER-STATION SYNC (Custom Q-Protocol) &nbsp;• 0ms TELEPORTATION &nbsp;• Q-NO CLONING DEFENSE</div>
                </div>
            </div>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="right-col">

            <!-- Haptic Force Graph -->
            <div class="graph-panel orange">
                <div class="panel-top">
                    <div class="panel-title">Haptic Force Applied (mN)</div>
                    <div class="panel-val orange" id="force-val">0</div>
                </div>
                <div class="graph-area">
                    <svg id="force-svg" preserveAspectRatio="none"></svg>
                </div>
            </div>

            <!-- Quantum Integrity Graph -->
            <div class="graph-panel green">
                <div class="panel-top">
                    <div class="panel-title">Quantum Link Integrity (1-QBER%)</div>
                    <div class="panel-val green" id="integrity-val">99</div>
                </div>
                <div class="graph-area">
                    <svg id="integrity-svg" preserveAspectRatio="none"></svg>
                </div>
            </div>

            <!-- Quantum Fail-Safe Box -->
            <div class="failsafe-panel">
                <div class="failsafe-tag">QUANTUM FAIL-SAFE</div>
                <div class="fs-row green"  id="qber-row">QBER [Error Rate]: 0.72%</div>
                <div class="fs-row cyan"   id="stab-row">LINK STABILITY: 98.1%</div>
                <div class="fs-row"        id="qec-row">QEC: ACTIVE &nbsp;&nbsp; Repairs: 12610</div>
                <div class="secure-badge">SECURE</div>
            </div>

        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer-bar">

        <!-- Block 1: Joystick Coords -->
        <div class="footer-block">
            <div class="joystick-pad">
                <div class="joy-dot" id="joy-dot" style="left:42%;top:54%"></div>
            </div>
            <div class="footer-text">
                <div class="ft-label">Haptic Coordinate Stream</div>
                <div class="ft-val" id="coord-val">X: 154 | Y: 102</div>
            </div>
        </div>

        <!-- Block 2: Protocol -->
        <div class="footer-block" style="flex-direction:column; align-items:flex-start; justify-content:center; gap:2px;">
            <div class="ft-label">PROTOCOL: STANDARD: Q-UDP/ENC</div>
            <div class="ft-route" id="route-val">CLASSICAL ROUTE</div>
            <div class="ft-sub"  id="delay-val">R-DELAY: 257 ms</div>
            <div class="ft-sub2" id="sync-val">SYNC RATE: 99.20%</div>
        </div>

        <!-- Block 3: QML -->
        <div class="footer-block" style="flex-direction:column; align-items:flex-start; justify-content:center; gap:2px;">
            <div class="qml-badge">QML ADVANTAGE</div>
            <div class="ft-label" style="margin:0;">QUANTUM PREDICTION</div>
            <div class="ft-disabled">PRED DISABLED</div>
            <div class="ft-sub" style="color:#718096; font-size:0.62rem;">[P] ACTIVATE AI &nbsp;|&nbsp; Expert Mode: Offline</div>
        </div>

    </div>

    <script>
        // --- Live data histories ---
        const HISTORY = 60;
        let forceData     = Array(HISTORY).fill(0);
        let integrityData = Array(HISTORY).fill(99);
        let repairs = 12610;

        function drawLine(svgId, data, color, maxVal) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            const W = svg.clientWidth  || 300;
            const H = svg.clientHeight || 90;
            const pts = data.map((v, i) => {
                const x = (i / (HISTORY - 1)) * W;
                const y = H - ((v / maxVal) * (H - 10)) - 2;
                return `${x},${Math.max(2, Math.min(H-2, y))}`;
            }).join(' ');
            svg.innerHTML = `<polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round"/>`;
        }

        function update() {
            // Simulate values
            const force    = Math.floor(Math.random() * 12);
            const integrity = 97 + Math.random() * 2.5;
            const qber     = (100 - integrity).toFixed(2);
            const stability = (97 + Math.random() * 2).toFixed(1);
            const delay    = 250 + Math.floor(Math.random() * 15);
            const rx       = 150 + Math.floor(Math.random() * 10);
            const ry       = 100 + Math.floor(Math.random() * 10);
            repairs += Math.floor(Math.random() * 8);

            // Push to history
            forceData.push(force);          forceData.shift();
            integrityData.push(integrity);  integrityData.shift();

            // Update dom
            document.getElementById('force-val').textContent   = force;
            document.getElementById('integrity-val').textContent = Math.round(integrity);
            document.getElementById('qber-row').textContent    = `QBER [Error Rate]: ${qber}%`;
            document.getElementById('stab-row').textContent    = `LINK STABILITY: ${stability}%`;
            document.getElementById('qec-row').textContent     = `QEC: ACTIVE    Repairs: ${repairs}`;
            document.getElementById('coord-val').textContent   = `X: ${rx} | Y: ${ry}`;
            document.getElementById('delay-val').textContent   = `R-DELAY: ${delay} ms`;

            // Joystick dot
            const dot = document.getElementById('joy-dot');
            dot.style.left = ((rx - 145) / 20 * 80 + 10) + '%';
            dot.style.top  = (100 - ((ry - 95) / 20 * 80 + 10)) + '%';

            // Draw graphs
            drawLine('force-svg',     forceData,     '#FFB432', 30);
            drawLine('integrity-svg', integrityData, '#64FF96', 100);
        }

        update();
        setInterval(update, 150);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
