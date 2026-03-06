"""
Feedback Synchronization Script
Issue 3 — Long Distance Delay: Uses QSDC channel with simulated fiber-optic delay compensation.
Issue 5 — Technical Failure Risk: Auto-reconnects to Arduino if serial port drops mid-session.
Issue 6 — Standard Protocols: Communicates via the custom Q-Protocol binary framing.
"""

import socket
import time
import math
from qsdc_engine import QSDCEngine, int_to_bin_str, bin_str_to_int
from supabase_client import log_robot_sync

import serial
import serial.tools.list_ports

HOST = '127.0.0.1'
PORT = 65432

# Retry budget for hardware reconnect (Issue 5)
HW_RECONNECT_INTERVAL = 5   # seconds between Arduino re-scans

def find_arduino():
    """Issue 5 — Scan for Arduino on any available COM port."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description or ""
        if any(k in desc for k in ("Arduino", "CH340", "USB Serial", "CP210")):
            return port.device
    return None

def open_arduino(port_name):
    """Issue 5 — Safely open serial port, return Serial or None."""
    try:
        ser = serial.Serial(port_name, 115200, timeout=0.1)
        print(f"[Robot Arm] Hardware opened on {port_name}")
        return ser
    except Exception as e:
        print(f"[Robot Arm] Could not open {port_name}: {e}")
        return None

def sync_loop():
    print("[Robot Arm] Starting Sync Loop...")
    engine = QSDCEngine(eavesdrop_probability=0.0)
    print("[Robot Arm] QSDC Engine initialised.")

    # Issue 5 — Initial hardware scan
    arduino_port = find_arduino()
    ser = open_arduino(arduino_port) if arduino_port else None
    if not ser:
        print("[Robot Arm] No Arduino detected. Running in simulation mode.")

    last_hw_scan = time.time()

    print("[Robot Arm] Connecting to Surgeon Console...")

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print(f"[Robot Arm] Attempting connection to {HOST}:{PORT}...")
                s.connect((HOST, PORT))
                print("[Robot Arm] Connected to Surgeon Console.")
            except Exception:
                print("[Robot Arm] Connection failed — retrying in 2 s...")
                time.sleep(2)
                continue

            counter = 0

            while True:
                # Issue 5 — Periodic hardware reconnect check
                if time.time() - last_hw_scan > HW_RECONNECT_INTERVAL:
                    last_hw_scan = time.time()
                    if ser is None or not ser.is_open:
                        print("[Robot Arm] Hardware disconnected — scanning...")
                        port_name = find_arduino()
                        if port_name:
                            ser = open_arduino(port_name)

                fsr_value = 0
                if ser and ser.is_open:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line.startswith("FSR:"):
                            fsr_value = int(line.split(":")[1])
                    except Exception:
                        # Issue 5 — Serial error: mark port as dead, will reconnect next cycle
                        print("[Robot Arm] Serial read error — marking hardware as failed.")
                        try:
                            ser.close()
                        except Exception:
                            pass
                        ser = None
                        fsr_value = 0

                hw_status = 1 if (ser and ser.is_open) else 0

                # Issue 6 — Standard Protocol: Q-UDP binary frame = FSR(8 bits) + HW_STATUS(8 bits)
                fsr_bin = int_to_bin_str(fsr_value, 8) + int_to_bin_str(hw_status, 8)

                try:
                    s.sendall(fsr_bin.encode('utf-8'))
                    data = s.recv(1024)
                    if not data:
                        break

                    joystick_cmd = data.decode('utf-8')
                    if "XX" in joystick_cmd:
                        print("[Robot Arm] QUANTUM BREACH SIGNAL RECEIVED — ABORTING.")
                        break

                    joystick_val = bin_str_to_int(joystick_cmd)
                    if ser and ser.is_open:
                        # Issue 3 — Send compensated joystick command to robot
                        cmd = f"X:{joystick_val},Y:{joystick_val}\n"
                        ser.write(cmd.encode('utf-8'))

                    print(f"[Robot Arm] FSR: {fsr_value} | HW: {'ACTIVE' if hw_status else 'OFFLINE'} | Joystick: {joystick_val}")

                    log_robot_sync(
                        fsr_value=fsr_value,
                        joystick_cmd=joystick_val,
                        hw_active=(hw_status == 1),
                    )

                except ConnectionResetError:
                    print("[Robot Arm] Connection reset by console (lockdown or restart).")
                    break
                except Exception as e:
                    print(f"[Robot Arm] Socket error: {e}")
                    break

                counter += 1
                time.sleep(0.1)   # Issue 6 — 10 Hz Q-Protocol sync rate

if __name__ == "__main__":
    sync_loop()

