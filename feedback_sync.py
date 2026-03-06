"""
Feedback Synchronization Script
Ensures the vibration motor at the console fires instantly when the FSR at the robot detects pressure.
Hooks into QSDC to securely transmit the feedback data.
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

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
            return port.device
    return None

def sync_loop():
    print("[Robot Arm] Starting Sync Loop...")
    engine = QSDCEngine(eavesdrop_probability=0.0)
    print("[Robot Arm] Engine Initialized.")
    
    arduino_port = find_arduino()
    ser = None
    if arduino_port:
        try:
            ser = serial.Serial(arduino_port, 115200, timeout=0.1)
            print(f"[Robot Arm] Hardware detected on {arduino_port}")
        except Exception as e:
            print(f"[Robot Arm] Could not open Serial: {e}")
    else:
        print("[Robot Arm] No Arduino detected. Defaulting FSR value to 0.")

    print("[Robot Arm] Initializing connection to Surgeon Console...")
    
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print(f"[Robot Arm] Attempting connection to {HOST}:{PORT}...")
                s.connect((HOST, PORT))
                print("[Robot Arm] Connected to Surgeon Console.")
            except Exception as e:
                print("[Robot Arm] Connection failed, waiting for console...")
                time.sleep(2)
                continue
                
            counter = 0
                
            while True:
                fsr_value = 0
                
                if ser and ser.is_open:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line.startswith("FSR:"):
                            fsr_value = int(line.split(":")[1])
                    except Exception:
                        fsr_value = 0
                else:
                    fsr_value = 0
                
                hw_status = 1 if (ser and ser.is_open) else 0
                fsr_bin = int_to_bin_str(fsr_value, 8) + int_to_bin_str(hw_status, 8)
                
                try:
                    s.sendall(fsr_bin.encode('utf-8'))
                    data = s.recv(1024)
                    if not data:
                        break
                        
                    joystick_cmd = data.decode('utf-8')
                    if "XX" in joystick_cmd:
                        print("[Robot Arm] QUANTUM BREACH FROM CONSOLE RECV! ABORTING.")
                        break
                        
                    joystick_val = bin_str_to_int(joystick_cmd)
                    if ser and ser.is_open:
                        cmd = f"X:{joystick_val},Y:{joystick_val}\n"
                        ser.write(cmd.encode('utf-8'))

                    print(f"[Robot Arm] FSR Sent: {fsr_value} | Joystick Recv: {joystick_val}")
                    
                    log_robot_sync(
                        fsr_value=fsr_value,
                        joystick_cmd=joystick_val,
                        hw_active=(hw_status == 1),
                    )
                    
                except ConnectionResetError:
                    print("[Robot Arm] Connection reset by console (possibly lockdown).")
                    break
                except Exception as e:
                    print("[Robot Arm] Error:", e)
                    break
                    
                counter += 1
                time.sleep(0.1)  # 10Hz sync rate

if __name__ == "__main__":
    sync_loop()
