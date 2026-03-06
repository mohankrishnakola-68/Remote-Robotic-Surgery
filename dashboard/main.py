from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import random
import time

app = FastAPI(title="Haptic-Q Tele-Operation Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAPTIC-Q // PRO SURGICAL CONSOLE</title>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00F5D4;
            --secondary: #7B61FF;
            --accent: #FF2E63;
            --bg-dark: #05070A;
            --card-bg: rgba(10, 15, 25, 0.8);
            --border-glow: rgba(0, 245, 212, 0.4);
            --text-main: #FFFFFF;
            --text-dim: #718096;
            --border-dim: rgba(255, 255, 255, 0.08);
            --force-orange: #FFA500;
            --integrity-green: #00FF9C;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Space Grotesk', sans-serif;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(123, 97, 255, 0.03) 0%, transparent 100%),
                linear-gradient(var(--border-dim) 1px, transparent 1px),
                linear-gradient(90deg, var(--border-dim) 1px, transparent 1px);
            background-size: 100% 100%, 60px 60px, 60px 60px;
        }

        /* Top Header */
        .header {
            height: 70px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 40px;
            border-bottom: 1px solid var(--border-dim);
            backdrop-filter: blur(10px);
            z-index: 100;
        }

        .sys-title {
            font-family: 'Michroma', sans-serif;
            font-size: 1.4rem;
            letter-spacing: 4px;
            color: white;
            text-shadow: 0 0 20px rgba(255,255,255,0.2);
        }

        .link-status {
            text-align: right;
        }
        .link-status .secure {
            color: var(--primary);
            font-family: 'Michroma';
            font-size: 1.1rem;
            letter-spacing: 2px;
            display: block;
        }
        .link-status .fail-safe {
            font-family: 'IBM Plex Mono';
            font-size: 0.7rem;
            color: var(--integrity-green);
            letter-spacing: 1px;
            margin-top: 4px;
        }

        /* Main Workspace */
        .workspace {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 400px;
            grid-template-rows: 1fr auto;
            gap: 20px;
            padding: 20px;
            max-width: 2000px;
            margin: 0 auto;
            width: 100%;
        }

        /* Left Side: Video & Pillars */
        .video-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .video-box {
            flex: 1;
            background: rgba(0,0,0,0.4);
            border: 2px solid var(--primary);
            position: relative;
            box-shadow: inset 0 0 50px rgba(0, 245, 212, 0.1);
        }

        .innovation-pillars {
            background: rgba(0, 245, 212, 0.05);
            border: 1px solid var(--primary);
            border-radius: 8px;
            padding: 12px 25px;
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .pillar-dot {
            width: 12px; height: 12px;
            background: var(--primary);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--primary);
        }
        .pillar-header {
            font-family: 'Michroma';
            font-size: 1.0rem;
            color: var(--primary);
            letter-spacing: 2px;
        }
        .pillar-content {
            font-family: 'Space Grotesk';
            font-size: 0.9rem;
            color: #E2E8F0;
            letter-spacing: 1px;
        }

        /* Right Side: Graphs & Fail-Safe */
        .telemetry-stack {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .glass-panel {
            background: var(--card-bg);
            border: 1px solid var(--border-dim);
            border-radius: 8px;
            padding: 20px;
            position: relative;
            backdrop-filter: blur(10px);
        }
        .glass-panel:hover { border-color: rgba(255,255,255,0.2); }

        .panel-label {
            font-family: 'Space Grotesk';
            color: #FFFFFF;
            font-size: 1.2rem;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-weight: 600;
        }
        .panel-label span { color: var(--primary); font-family: 'IBM Plex Mono'; font-weight: 800; }

        .graph-area {
            height: 120px;
            border-left: 1px solid rgba(255,255,255,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: flex-end;
            gap: 4px;
            background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        .bar { flex: 1; transition: height 0.3s ease; }

        /* Quantum Fail-Safe Detail Box */
        .fail-safe-box {
            border: 1px solid var(--primary);
            border-radius: 4px;
            padding: 15px;
            margin-top: 10px;
            position: relative;
        }
        .fail-safe-header {
            position: absolute;
            top: -14px; left: 10px;
            background: var(--bg-dark);
            padding: 0 12px;
            font-family: 'Michroma';
            font-size: 0.8rem;
            color: var(--primary);
        }
        .fs-metric {
            font-family: 'IBM Plex Mono';
            font-size: 1.1rem;
            color: #FFFFFF;
            margin-bottom: 10px;
        }
        .secure-badge {
            position: absolute;
            right: 15px;
            bottom: 15px;
            font-family: 'Michroma';
            font-size: 0.9rem;
            color: var(--primary);
        }

        /* Footer Console */
        .footer-console {
            grid-column: 1 / span 2;
            height: 100px;
            background: rgba(10, 15, 25, 0.9);
            border: 1px solid var(--border-dim);
            display: grid;
            grid-template-columns: 350px 1fr 350px;
            gap: 1px;
            background: var(--border-dim);
        }

        .footer-block {
            background: var(--bg-dark);
            padding: 15px 25px;
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .coord-grid {
            width: 60px; height: 60px;
            border: 1px solid rgba(255,255,255,0.2);
            position: relative;
        }
        .coord-grid::before, .coord-grid::after {
            content: ''; position: absolute;
            background: rgba(255,255,255,0.1);
        }
        .coord-grid::before { left: 50%; top: 0; width: 1px; height: 100%; }
        .coord-grid::after { top: 50%; left: 0; height: 1px; width: 100%; }
        .coord-dot {
            position: absolute;
            width: 6px; height: 6px;
            background: var(--primary);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 10px var(--primary);
        }

        .block-title {
            font-family: 'Space Grotesk';
            font-size: 0.8rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 5px;
        }
        .block-val {
            font-family: 'Michroma';
            font-size: 1.25rem;
            color: white;
        }
 
        .protocol-tag {
            color: var(--accent);
            font-family: 'Michroma';
            font-size: 1.0rem;
            margin-top: 5px;
        }
        .protocol-sub {
            font-family: 'IBM Plex Mono';
            font-size: 0.8rem;
            color: var(--accent);
            opacity: 1.0;
        }

        .ai-status {
            background: var(--secondary);
            color: white;
            font-family: 'Space Grotesk';
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 2px;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="sys-title">HAPTIC-Q SURGEON CONSOLE</div>
        <div class="link-status">
            <span class="secure">SECURE LINK: ACTIVE</span>
            <span class="fail-safe">[ FAIL-SAFE: READY ]</span>
        </div>
    </header>

    <main class="workspace">
        <div class="video-container">
            <div class="video-box">
                <div style="position: absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; color:rgba(255,255,255,0.2);">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.0">
                        <path d="M15 10l5 5-5 5M4 14h16"/>
                    </svg>
                    <div style="font-family: 'Michroma'; font-size: 1.0rem; margin-top: 15px; color: var(--primary); letter-spacing: 2px;">LIVE_SURGICAL_STREAM</div>
                    <div style="font-family: 'IBM Plex Mono'; font-size: 0.8rem; color: #718096; margin-top: 5px;">[ WAITING FOR ENCRYPTED HANDSHAKE... ]</div>
                </div>
            </div>
            
            <div class="innovation-pillars">
                <div class="pillar-dot"></div>
                <div>
                    <div class="pillar-header">HACKATHON INNOVATION PILLARS</div>
                    <div class="pillar-content">
                        • INTER-STATION SYNC (Custom Q-Protocol) • 0ms TELEPORTATION • Q-NO CLONING DEFENSE
                    </div>
                </div>
            </div>
        </div>

        <div class="telemetry-stack">
            <div class="glass-panel">
                <div class="panel-label">Haptic Force Applied (mN) <span id="f-val-top">0</span></div>
                <div class="graph-area" id="force-graph"></div>
            </div>

            <div class="glass-panel">
                <div class="panel-label">Quantum Link Integrity (1-QBER %) <span id="i-val-top">99</span></div>
                <div class="graph-area" id="integrity-graph"></div>
            </div>

            <div class="glass-panel" style="padding: 10px;">
                <div class="fail-safe-box">
                    <div class="fail-safe-header">QUANTUM FAIL-SAFE</div>
                    <div class="fs-metric" id="qber-val">QBER [Error Rate]: 0.37%</div>
                    <div class="fs-metric" id="stab-val">LINK STABILITY: 99.1%</div>
                    <div class="fs-metric" id="qec-val">QEC REPAIR: ACTIVE | Repairs: 5182</div>
                    <div class="secure-badge">SECURE</div>
                </div>
            </div>
        </div>

        <div class="footer-console">
            <div class="footer-block">
                <div class="coord-grid">
                    <div class="coord-dot" id="dot"></div>
                </div>
                <div>
                    <div class="block-title">Haptic Coordinate Stream</div>
                    <div class="block-val" id="coord-val">X: 154 | Y: 102</div>
                </div>
            </div>

            <div class="footer-block" style="flex-direction: column; align-items: flex-start; justify-content: center; gap: 0;">
                <div class="block-title">PROTOCOL: STANDARD: Q-UDP/ENC</div>
                <div class="protocol-tag">CLASSICAL ROUTE</div>
                <div class="protocol-sub" id="delay-val">R-DELAY: 276 ms | SYNC RATE: 99.67%</div>
            </div>

            <div class="footer-block" style="flex-direction: column; align-items: flex-start; justify-content: center; gap: 5px;">
                <div class="ai-status">QML ADVANTAGE</div>
                <div class="block-title" style="margin: 0;">QUANTUM PREDICTION</div>
                <div class="block-val" style="font-size: 0.9rem;">PRED DISABLED</div>
                <div style="font-family: 'Space Grotesk'; font-size: 0.6rem; color: var(--text-dim);">[P] ACTIVATE AI | Expert Mode: Offline</div>
            </div>
        </div>
    </main>

    <script>
        const fGraph = document.getElementById('force-graph');
        const iGraph = document.getElementById('integrity-graph');
        
        for(let i=0; i<30; i++) {
            fGraph.innerHTML += `<div class="bar" style="background: var(--force-orange); opacity: 0.6; height: ${Math.random()*40+20}%"></div>`;
            iGraph.innerHTML += `<div class="bar" style="background: var(--integrity-green); opacity: 0.7; height: ${Math.random()*20+70}%"></div>`;
        }

        function updateTelemetry() {
            const rx = 150 + Math.floor(Math.random()*10);
            const ry = 100 + Math.floor(Math.random()*10);
            const fVal = Math.floor(Math.random()*10);
            const iVal = 99 + Math.floor(Math.random()*1);
            const delay = 270 + Math.floor(Math.random()*10);
            const repairs = 5180 + Math.floor(Math.random()*20);

            document.getElementById('coord-val').innerText = `X: ${rx} | Y: ${ry}`;
            document.getElementById('f-val-top').innerText = fVal;
            document.getElementById('i-val-top').innerText = iVal;
            document.getElementById('delay-val').innerText = `R-DELAY: ${delay} ms | SYNC RATE: 99.67%`;
            document.getElementById('qec-val').innerText = `QEC REPAIR: ACTIVE | Repairs: ${repairs}`;

            const dot = document.getElementById('dot');
            dot.style.left = (rx - 150) * 5 + 30 + 'px';
            dot.style.top = (ry - 100) * 5 + 30 + 'px';

            const fbars = fGraph.querySelectorAll('.bar');
            const ibars = iGraph.querySelectorAll('.bar');
            fbars.forEach(b => b.style.height = (Math.random() * 50 + 10) + '%');
            ibars.forEach(b => b.style.height = (Math.random() * 10 + 85) + '%');
        }

        setInterval(updateTelemetry, 150);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
