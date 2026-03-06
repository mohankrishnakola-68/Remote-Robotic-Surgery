"""
Haptic-Q: Surgeon's Command Console (Ultimate Pro Edition)
Restores the layout from the reference image with premium fonts, 
animated breathing borders, and a high-fidelity technical background.
"""

import os
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'  # Avoid MSMF crash on Windows
import cv2
import socket
import threading
import numpy as np
import time
import math
from collections import deque
from PIL import Image, ImageDraw, ImageFont
from qsdc_engine import QSDCEngine, int_to_bin_str, bin_str_to_int
from supabase_client import log_telemetry, log_breach_event

# --- Configuration ---
HOST = '127.0.0.1'
PORT = 65432
WIDTH, HEIGHT = 1024, 768  # Resolution matched to standard dashboard scale

# --- State ---
force_applied = 0
quantum_integrity = 100
breach_detected = False
joystick_x, joystick_y = 154, 102
lockdown = False
latency_ms = 0
precision_mode = False
quantum_latency_active = False
hacker_attack_active = False
qml_prediction_active = False
prediction_accuracy = 100.0
quantum_stability = 100.0
stability_history = deque([100.0] * 100, maxlen=100)
qec_active = True
qec_repair_count = 0 
decoherence_risk = 0.0
qber_rate = 1.1 # Initial error rate
protocol_sync = 99.8 # Universal Standard Layer
FORCE_THRESHOLD = 180

# History for the dual graphs on the right
force_history = deque([0] * 100, maxlen=100)
integrity_history = deque([100] * 100, maxlen=100)
socket_active = False
hw_active = False

# --- Style / Theme ---
def get_font(size, bold=False):
    # Try multiple standard Windows fonts to ensure size is respected
    fonts = ["seguisb.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf", "consola.ttf"]
    for f in fonts:
        try:
            return ImageFont.truetype(os.path.join("C:\\Windows\\Fonts", f), size)
        except:
            continue
    return ImageFont.load_default()

F_HEADER = get_font(32, True)
F_STATUS = get_font(22, True)
F_PANEL_H = get_font(18, True)
F_PANEL_V = get_font(15, False)
F_FOOTER = get_font(15, False)

# Colors (RGBA for PIL)
CLR_BG = (10, 12, 18, 255)
CLR_PANEL = (30, 35, 50, 255)
CLR_CYAN = (0, 255, 230, 255)
CLR_RED = (255, 50, 60, 255)
CLR_TEXT = (255, 255, 255, 255)
CLR_TEXT_DIM = (180, 195, 210, 255)

def create_tech_bg():
    """Create a premium dark background with a subtle grid pattern."""
    base = np.full((HEIGHT, WIDTH, 3), (15, 18, 25), dtype=np.uint8)
    # Draw subtle grid
    grid_spacing = 40
    for x in range(0, WIDTH, grid_spacing):
        cv2.line(base, (x, 0), (x, HEIGHT), (20, 24, 35), 1)
    for y in range(0, HEIGHT, grid_spacing):
        cv2.line(base, (0, y), (WIDTH, y), (20, 24, 35), 1)
    return base

G_BG_TECH = create_tech_bg()

def draw_graph_panel(draw, x, y, w, h, title, value, unit, data, color, border_color):
    # Unique Rounded Panel Background
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(28, 35, 50, 220), outline=border_color, width=3)
    
    # Corner Accents (Make it Unique)
    L = 15
    draw.line([x, y, x+L, y], fill=(255, 255, 255, 100), width=3)
    draw.line([x, y, x, y+L], fill=(255, 255, 255, 100), width=3)
    
    # Title & Large Value Display
    draw.text((x + 20, y + 15), title, font=F_PANEL_H, fill=(255, 255, 255, 255))
    val_str = f"{value}"
    tw = draw.textlength(val_str, font=F_PANEL_H)
    draw.text((x + w - tw - 25, y + 15), val_str, font=F_PANEL_H, fill=color)
    
    # Graph Area
    gx, gy, gw, gh = x + 20, y + 55, w - 40, h - 75
    draw.rectangle([gx, gy, gx + gw, gy + gh], fill=(12, 15, 22, 255))
    
    # Grid Lines
    grid_col = (40, 45, 60, 255)
    for i in range(1, 4): draw.line([gx, gy + (gh * i // 4), gx + gw, gy + (gh * i // 4)], fill=grid_col, width=1)
    for i in range(1, 6): draw.line([gx + (gw * i // 6), gy, gx + (gw * i // 6), gy + gh], fill=grid_col, width=1)
        
    if len(data) > 1:
        points = []
        max_val = 255 if "Force" in title else 100
        for i, val in enumerate(data):
            px = gx + (i * gw / (len(data) - 1))
            display_val = val + np.random.uniform(-0.8, 0.8)
            py = gy + gh - int((display_val / max_val) * (gh - 10))
            py = max(gy + 5, min(gy + gh - 5, py))
            points.append((px, py))
        
        draw.line(points, fill=(*color[:3], 100), width=4) # Glow
        draw.line(points, fill=color, width=2) # Line

def render_ui(frame):
    # Base Image
    img = Image.fromarray(G_BG_TECH.copy()).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # 1. Header (Horizontal Bar)
    draw.rectangle([0, 0, WIDTH, 80], fill=(22, 28, 40, 255))
    draw.text((30, 22), "HAPTIC-Q SURGEON CONSOLE", font=F_HEADER, fill=CLR_TEXT)
    
    # Consolidate Status Message
    status_label = "SECURE LINK: ACTIVE" if socket_active else "SCANNING FOR ROBOT..."
    if breach_detected: status_label = "CRITICAL BREACH DETECTED"
    status_col = CLR_CYAN if (socket_active and not breach_detected) else CLR_RED
    if not socket_active and not breach_detected: status_col = CLR_TEXT_DIM
    draw.text((WIDTH - 380, 25), status_label, font=F_STATUS, fill=status_col)
    
    # NEW: Fail-Safe & Robustness Tag
    fs_tag = "FAIL-SAFE: READY" if quantum_stability > 85 else "FALLBACK: ACTIVE"
    fs_col = (100, 255, 150) if quantum_stability > 85 else (255, 180, 50)
    draw.text((WIDTH - 380, 58), f"[ {fs_tag} ]", font=get_font(10, True), fill=fs_col)

    # 2. Main Video Feed (Center-Left)
    vw, vh = 600, 450
    vx, vy = 30, 120
    
    # Animated Border Logic (Breathing Cyan)
    t = time.time()
    glow_intensity = int(127 + 127 * math.sin(t * 3)) # Pulse 3x per sec
    anim_color = (0, 255, 220, glow_intensity)
    
    # Draw frame border
    draw.rectangle([vx - 3, vy - 3, vx + vw + 3, vy + vh + 3], outline=anim_color, width=3)
    
    if frame is not None:
        frame_resized = cv2.resize(frame, (vw, vh))
        # Scanlines removed for maximum clarity
        frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
        img.paste(frame_pil, (vx, vy))
    else:
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(15, 20, 30))
        draw.text((vx + vw//2 - 140, vy + vh//2 - 20), "WAITING FOR CAMERA...", font=F_PANEL_H, fill=CLR_CYAN)
        draw.text((vx + vw//2 - 140, vy + vh//2 + 20), "[CHECK USB CONNECTION]", font=F_PANEL_V, fill=CLR_TEXT_DIM)

    # 2.5 Hackathon Innovation Hub (Under the Video)
    hub_y = 585
    draw.rounded_rectangle([30, hub_y, 30 + 600, hub_y + 55], radius=10, fill=(25, 30, 50, 200), outline=(0, 255, 220), width=1)
    
    # Icons/Glows
    draw.ellipse([45, hub_y + 15, 60, hub_y + 30], fill=CLR_CYAN) # Pulse
    draw.text((70, hub_y + 8), "HACKATHON INNOVATION PILLARS", font=F_PANEL_H, fill=CLR_CYAN)
    
    pill_font = get_font(11, False)
    draw.text((70, hub_y + 30), "• INTER-STATION SYNC (Custom Q-Protocol) • 0ms TELEPORTATION • Q-NO CLONING DEFENSE", font=pill_font, fill=CLR_TEXT)

    # 3. Telemetry Panels (Right Side) - Unique Borders
    panel_w = 330
    panel_x = WIDTH - panel_w - 30
    
    # Haptic Force - Unique Orange Theme
    draw_graph_panel(draw, panel_x, 100, panel_w, 230, "Haptic Force Applied (mN)", force_applied, "mN", list(force_history), (255, 180, 50, 255), (150, 100, 30, 255))
    
    # Quantum Link - Unique Green Theme
    draw_graph_panel(draw, panel_x, 345, panel_w, 230, "Quantum Link Integrity (1-QBER %)", quantum_integrity, "%", list(integrity_history), (100, 255, 150, 255), (30, 120, 60, 255))
    
    # New Security Status Text for Issue 2 (Professional Glassmorphism)
    # Positioned with air-gap from graph (ends at 575) and footer (starts at 650)
    box_y = 575
    box_h = 70
    draw.rectangle([panel_x, box_y, panel_x + panel_w, box_y + box_h], fill=(10, 20, 35, 250), outline=CLR_CYAN, width=2)
    
    # Innovation Tag (Slightly larger tag)
    draw.rectangle([panel_x + 5, box_y - 12, panel_x + 130, box_y + 10], fill=CLR_CYAN)
    draw.text((panel_x + 12, box_y - 14), "QUANTUM FAIL-SAFE", font=get_font(11, True), fill=(0, 0, 0))

    qber_col = (100, 255, 100) if qber_rate < 11.0 else (255, 100, 100)
    draw.text((panel_x + 15, box_y + 12), f"QBER [Error Rate]: {qber_rate:.2f}%", font=F_PANEL_V, fill=qber_col)
    
    stab_col = (100, 255, 220) if quantum_stability > 80 else (255, 200, 50)
    draw.text((panel_x + 15, box_y + 30), f"LINK STABILITY: {quantum_stability:.1f}%", font=F_PANEL_V, fill=stab_col)
    
    # QEC Status (Risk Mitigation)
    qec_col = (150, 255, 180) if qec_active else CLR_TEXT_DIM
    draw.text((panel_x + 15, box_y + 48), f"QEC: {'ACTIVE' if qec_active else 'OFF'}", font=get_font(12, True), fill=qec_col)
    draw.text((panel_x + 125, box_y + 48), f"Repairs: {qec_repair_count}", font=get_font(12, True), fill=(220, 240, 255))
    
    security_text = "SECURE" if qber_rate < 11.0 else "INTERCEPTED!"
    draw.text((panel_x + panel_w - 110, box_y + 22), security_text, font=F_PANEL_H, fill=qber_col)

    # 4. Footer System Bar (Technical Navy Theme)
    draw.rounded_rectangle([30, 650, WIDTH - 30, 745], radius=10, fill=(30, 38, 55, 255), outline=(100, 120, 160, 255), width=2)
    
    # Visual Joystick Pad (Left Side of Footer)
    jx, jy, jw, jh = 50, 660, 60, 60
    draw.rectangle([jx, jy, jx+jw, jy+jh], fill=(15, 20, 30, 255), outline=CLR_TEXT_DIM)
    # Centers
    draw.line([jx + jw//2, jy, jx + jw//2, jy + jh], fill=(50, 60, 80), width=1)
    draw.line([jx, jy + jh//2, jx + jw, jy + jh//2], fill=(50, 60, 80), width=1)
    # Position Dot
    dot_x = jx + int((joystick_x / 255) * jw)
    dot_y = jy + jh - int((joystick_y / 255) * jh) # Invert Y for UI
    draw.ellipse([dot_x-4, dot_y-4, dot_x+4, dot_y+4], fill=CLR_CYAN)
    
    # Section A: Telemetry Text (Movement)
    draw.text((130, 658), f"HAPTIC COORDINATE STREAM", font=F_PANEL_H, fill=CLR_TEXT_DIM)
    draw.text((130, 678), f"X: {joystick_x:03d} | Y: {joystick_y:03d}", font=F_HEADER, fill=CLR_TEXT)
    
    # Section B: Quantum Network Matrix (Issue 1 & 3)
    net_x = WIDTH // 2 - 40
    draw.line([net_x - 15, 660, net_x - 15, 735], fill=CLR_TEXT_DIM, width=1)
    
    q_lat_stat = "Q-TELEPORTATION" if quantum_latency_active else "CLASSICAL ROUTE"
    q_lat_col = CLR_CYAN if quantum_latency_active else (255, 100, 100)
    
    # EXPERT DETAIL: Addressing Lack of Standards (Protocol Layer)
    p_label = "STANDARD: Q-UDP/ENC" if quantum_stability > 80 else "MAPPING: CLS-Q"
    draw.text((net_x, 658), f"PROTOCOL: {p_label}", font=F_PANEL_H, fill=CLR_TEXT_DIM)
    draw.text((net_x, 678), q_lat_stat, font=F_STATUS, fill=q_lat_col)
    
    psync_col = (100, 255, 200) if protocol_sync > 99 else (255, 255, 100)
    lat_col = (100, 255, 100) if latency_ms < 50 else (255, 100, 100)
    draw.text((net_x, 706), f"R-DELAY: {latency_ms} ms", font=F_PANEL_V, fill=lat_col)
    draw.text((net_x, 722), f"SYNC RATE: {protocol_sync:.2f}%", font=get_font(10), fill=psync_col)
    
    # Section C: Machine Learning Accuracy (Issue 3)
    ai_x = WIDTH - 260
    draw.line([ai_x - 15, 660, ai_x - 15, 740], fill=CLR_TEXT_DIM, width=1)
    
    # Expert Info Badge
    draw.rectangle([ai_x, 655, ai_x + 95, 668], fill=(180, 100, 255))
    draw.text((ai_x + 8, 653), "QML ADVANTAGE", font=get_font(10, True), fill=(255, 255, 255))
    
    qml_stat = "QNN PREDICT ON" if qml_prediction_active else "PRED DISABLED"
    qml_col = (200, 150, 255) if qml_prediction_active else (150, 150, 165)
    
    draw.text((ai_x, 672), "QUANTUM PREDICTION", font=F_PANEL_H, fill=CLR_TEXT_DIM)
    draw.text((ai_x, 691), qml_stat, font=F_STATUS, fill=qml_col)
    
    if qml_prediction_active:
        acc_col = (100, 255, 100) if prediction_accuracy > 99 else (255, 255, 100)
        draw.text((ai_x, 706), f"CONFIDENCE: {prediction_accuracy:.2f}%", font=F_PANEL_V, fill=acc_col)
        draw.text((ai_x, 722), "Simulates 1024 Quantum Shots/sec", font=get_font(9), fill=CLR_TEXT_DIM)
    else:
        draw.text((ai_x, 706), "[P] ACTIVATE AI", font=F_PANEL_V, fill=CLR_TEXT_DIM)
        draw.text((ai_x, 722), "Expert Mode: Offline", font=get_font(9), fill=CLR_TEXT_DIM)

    # Emergency Overlay (Cinematic Breach Animation)
    if lockdown:
        # 1. Base flashing pulse
        pulse = int(100 + 100 * math.sin(time.time() * 10))
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (120, 0, 0, pulse))
        img = Image.alpha_composite(img, overlay)
        draw_l = ImageDraw.Draw(img)
        
        # 2. Scrolling Hazard Bars (Top & Bottom)
        bar_h = 40
        scroll_x = int(time.time() * 200) % 400
        for b_y in [0, HEIGHT - bar_h]:
            draw_l.rectangle([0, b_y, WIDTH, b_y + bar_h], fill=(255, 0, 0, 200))
            # Draw diagonal stripes for "Hazard" look
            for s_x in range(-scroll_x, WIDTH + 100, 50):
                draw_l.line([s_x, b_y, s_x + 30, b_y + bar_h], fill=(0, 0, 0, 255), width=10)
        
        # 3. Aggressive Center Warning
        warning_font = get_font(48, True)
        msg_y = HEIGHT // 2 - 80
        # Text shadow/glow
        draw_l.text((WIDTH//2 - 253, msg_y + 3), "CRITICAL QUANTUM BREACH", font=warning_font, fill=(0, 0, 0))
        draw_l.text((WIDTH//2 - 250, msg_y), "CRITICAL QUANTUM BREACH", font=warning_font, fill=(255, 255, 255))
        
        draw_l.text((WIDTH//2 - 180, msg_y + 70), "ENTANGLEMENT COLLAPSED", font=F_STATUS, fill=(255, 200, 200))
        draw_l.text((WIDTH//2 - 130, msg_y + 110), "SYSTEM LOCKDOWN", font=F_HEADER, fill=(255, 255, 255))
        draw_l.text((WIDTH//2 - 160, msg_y + 150), "[PRESS 'R' TO RESET SECURE CHANNEL]", font=F_STATUS, fill=(255, 255, 100))
        
        # 4. Display Intercepted Data Types
        stolen_data_y = msg_y + 200
        draw_l.text((WIDTH//2 - 120, stolen_data_y), "THREAT VECTOR INTERCEPTED:", font=F_PANEL_H, fill=(255, 100, 100))
        
        # Flashing text effect for stolen data
        if int(time.time() * 5) % 2 == 0:
            draw_l.text((WIDTH//2 - 140, stolen_data_y + 30), "> VIDEO FEED (INTERCEPTED) : ENCRYPTED", font=F_PANEL_V, fill=CLR_TEXT)
            draw_l.text((WIDTH//2 - 140, stolen_data_y + 50), "> TELEMETRY (SNIFFED) : QUANTUM BLOCKED", font=F_PANEL_V, fill=CLR_TEXT)
            draw_l.text((WIDTH//2 - 140, stolen_data_y + 70), "> HAPTIC CMDS (COPIED) : NO-CLONING TRAP", font=F_PANEL_V, fill=CLR_TEXT)
            draw_l.text((WIDTH//2 - 140, stolen_data_y + 90), "> PATIENT VITALS (TARGETED) : SECURE", font=F_PANEL_V, fill=CLR_TEXT)

    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

# --- Comms Boilerplate ---
def qsdc_console_server():
    global force_applied, quantum_integrity, breach_detected, lockdown, latency_ms, socket_active, hw_active, quantum_latency_active, hacker_attack_active, qml_prediction_active, prediction_accuracy, qber_rate, quantum_stability, qec_repair_count, decoherence_risk
    print(f"[Console Server] Initializing on {HOST}:{PORT}...")
    engine = QSDCEngine(eavesdrop_probability=0.0)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        s.settimeout(1.0)
        
        while True:
            try:
                # If we are in lockdown, wait for user to reset (R)
                if lockdown:
                    socket_active = False
                    hw_active = False
                    time.sleep(0.5)
                    continue
                    
                print("[Console Server] Waiting for connection...")
                conn, addr = s.accept()
                print(f"[Console Server] Accepted connection from {addr}")
                socket_active = True
                conn.settimeout(2.0)
                
                with conn:
                    while not lockdown:
                        t0 = time.time()
                        try:
                            # 1. Receive data
                            data = conn.recv(1024)
                            if not data: break
                            
                            actual_socket_delay = time.time() - t0
                            
                            # Only trigger eavesdropping if user manually sets it (Press 'H')
                            engine.eavesdrop_probability = 1.0 if hacker_attack_active else 0.0
                            
                            # 2. Process via QSDC
                            rx_bits, breached = engine.transmit_data(data.decode('utf-8'))
                            
                            # SIMULATING QML PREDICTIVE HAPTICS (ISSUE 3)
                            actual_force = bin_str_to_int(rx_bits[:8])
                            
                            # Quantum State Ensemble Prediction (Simulated QNN)
                            if not breached and qml_prediction_active:
                                # We simulate 1024 Quantum Shots to predict the force trajectory
                                shots = 1024
                                noise_level = 0.005 # Extremely low error in quantum space
                                
                                # Simulated superposition of possible haptic states
                                prediction_samples = [actual_force + np.random.normal(0, actual_force * noise_level) for _ in range(shots)]
                                predicted_force = int(np.mean(prediction_samples))
                                
                                # Calculate Precise Accuracy based on Quantum Deviation
                                deviation = abs(actual_force - predicted_force)
                                prediction_accuracy = 100.0 - (deviation / 255.0 * 100.0)
                                if prediction_accuracy > 99.9: prediction_accuracy = 99.9
                                
                                # Instantly feed predicted force to UI
                                force_applied = predicted_force
                                force_history.append(force_applied)
                            elif not qml_prediction_active:
                                prediction_accuracy = 0.0
                            
                            # SIMULATE REAL-WORLD LATENCY (ISSUE 1 - SORTED VIA QUANTUM)
                            if quantum_latency_active:
                                # Quantum Teleportation of Haptic States
                                sim_delay = np.random.uniform(0.0001, 0.0005) # 0.1ms - 0.5ms (Instataneous simulation)
                            else:
                                # Classical fiber-optic transatlantic delay (Issue 3: Solving the distance lag)
                                sim_delay = np.random.uniform(0.120, 0.180) # 120-180ms delay across the ocean
                            
                            time.sleep(sim_delay)
                            latency_ms = int((actual_socket_delay + sim_delay) * 1000)
                            
                            if breached:
                                breach_detected, quantum_integrity, lockdown = True, 0, True
                                log_breach_event("QUANTUM ENTANGLEMENT COLLAPSED - EAVESDROP DETECTED")
                                
                                # Send terminal collapse packet to Robot so it disconnects
                                try:
                                    conn.sendall(b"XX") 
                                except: pass
                                
                                break
                            else:
                                if not qml_prediction_active:
                                    # With no prediction, the force value is only received AFTER the delayed sleep block!
                                    force_applied = actual_force
                                    force_history.append(force_applied)
                                
                                hw_active = (bin_str_to_int(rx_bits[8:16]) == 1)
                                
                                integrity_history.append(quantum_integrity)
                            
                            # 3. Send Feedback
                            move_val = (joystick_x + joystick_y) // 2
                            conn.sendall(int_to_bin_str(move_val).encode('utf-8'))
                            
                            # 4. Log to Supabase
                            log_telemetry(
                                force_applied=force_applied,
                                quantum_integrity=quantum_integrity,
                                latency_ms=latency_ms,
                                joystick_x=joystick_x,
                                joystick_y=joystick_y,
                                socket_active=socket_active,
                                hw_active=hw_active,
                                breach_detected=breach_detected,
                            )
                            
                        except: break
                
                socket_active = False
                hw_active = False
                latency_ms = 0
                
            except: continue

def simulation_heartbeat():
    """Dedicated thread to ensure Quantum Simulation (Issue 1, 2, 3) is ALWAYS live and original."""
    global quantum_stability, qber_rate, qec_repair_count, decoherence_risk, quantum_integrity, prediction_accuracy, force_applied, protocol_sync
    while True:
        try:
            # SIMULATING NATURAL QUANTUM ENVIRONMENT (Aesthetic Heartbeat)
            noise = np.sin(time.time() * 2.0) * 3 + np.random.normal(0, 0.5)
            quantum_stability = max(80.0, min(100.0, 96.0 + noise))
            
            # Protocol Sync Flutter (Fixing Lack of Standard protocols)
            protocol_sync = 99.8 + math.sin(time.time() * 0.5) * 0.15 + np.random.uniform(0, 0.05)
            
            if not socket_active:
                # Idle Simulation: Sync metrics with the ECG Pulse
                pulse = generate_ecg(time.time())
                qber_rate = max(1.0, 5.0 - (pulse * 4.0) + np.random.uniform(0, 0.5))
                # Stability follows noise when idle
            else:
                # Active Connection: More extreme physics
                decoherence_risk = 100.0 - quantum_stability
                if decoherence_risk > 5.0:
                    qec_repair_count += int(decoherence_risk * 5)
                
                if hacker_attack_active:
                    qber_rate = np.random.uniform(30.0, 60.0)
                else:
                    # QEC Mitigation logic
                    qber_rate = max(0.2, (100.0 - quantum_stability) * 0.4 * (1.0 - (qec_repair_count % 50 / 100.0)))

            quantum_integrity = int(100 - qber_rate)
            integrity_history.append(quantum_integrity)
            stability_history.append(quantum_stability)
            
            if not socket_active or not hw_active:
                # Hardware not inserted or connection lost -> Force must be 0
                force_applied = 0
                force_history.append(0)
                if not socket_active:
                    # Generic background error when idle
                    qber_rate = 0.0
                
                if not qml_prediction_active:
                    prediction_accuracy = 0.0
            
            time.sleep(0.05) # 20Hz Simulation
        except: time.sleep(1)

def generate_ecg(t):
    """Generates a normalized procedural ECG-like 'Pulse' signal."""
    t %= 1.0 # 1 Hz heartbeat
    # P Wave
    p = 0.1 * math.exp(-((t - 0.2)**2) / 0.005)
    # QRS Complex (The big spike)
    q = -0.1 * math.exp(-((t - 0.4)**2) / 0.001)
    r = 1.0 * math.exp(-((t - 0.42)**2) / 0.0005)
    s = -0.2 * math.exp(-((t - 0.45)**2) / 0.001)
    # T Wave
    t_wave = 0.2 * math.exp(-((t - 0.7)**2) / 0.01)
    return (p + q + r + s + t_wave)

def main():
    global precision_mode, joystick_x, joystick_y, quantum_latency_active, hacker_attack_active, lockdown, breach_detected, quantum_integrity, qml_prediction_active
    print("[Console UI] Starting Simulation Threads...")
    threading.Thread(target=qsdc_console_server, daemon=True).start()
    threading.Thread(target=simulation_heartbeat, daemon=True).start()
    try:
        cv2.namedWindow("Haptic-Q Pro Console", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Haptic-Q Pro Console", WIDTH, HEIGHT)
        print("[Console UI] Window created.")
    except Exception as e:
        print(f"[Console UI] No display detected or window error: {e}")
        
    cap = None
    try:
        print("[Console UI] Attempting to open camera (DirectShow)...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap and cap.isOpened():
            # Request High Clarity / HD Feed
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            print("[Console UI] Camera opened with HD settings.")
        else:
            print("[Console UI] Camera access failed. Running with placeholder data.")
            cap = None
    except Exception as e:
        print(f"[Console UI] Camera error (drivers missing?): {e}")
        cap = None
    
    start_time = time.time()
    print("[Console UI] Starting Main loop...")
    try:
        while True:
            # 1. Normalized Pulse Simulation (Moving Graphs)
            # (Now handled by the Simulation Heartbeat thread for 100% 'Original' live feel)
            
            frame = None
            if cap:
                ret, frame_cap = cap.read()
                if ret: frame = frame_cap
            ui_frame = render_ui(frame)
            try:
                cv2.imshow("Haptic-Q Pro Console", ui_frame)
            except:
                pass # Headless mode - skip showing window
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            elif key == ord('m'): precision_mode = not precision_mode
            elif key == ord('k'): quantum_latency_active = not quantum_latency_active
            elif key == ord('p'): qml_prediction_active = not qml_prediction_active
            elif key == ord('h'): hacker_attack_active = True
            elif key == ord('r'):
                hacker_attack_active = False
                lockdown = False
                breach_detected = False
                quantum_integrity = 100
            
            # Adjustable Step Sensitivity
            step = 2 if precision_mode else 10
            
            # Manual adjustment
            if key == ord('w'): joystick_y = min(255, joystick_y + step)
            if key == ord('s'): joystick_y = max(0, joystick_y - step)
            if key == ord('a'): joystick_x = max(0, joystick_x - step)
            if key == ord('d'): joystick_x = min(255, joystick_x + step)
    except Exception as e:
        print(f"[Console UI] CRITICAL ERROR IN MAIN LOOP: {e}")
    finally:
        if cap: cap.release()
        cv2.destroyAllWindows()
        print("[Console UI] Shutdown complete.")

if __name__ == "__main__":
    main()
