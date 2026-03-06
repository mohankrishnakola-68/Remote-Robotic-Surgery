"""
Haptic-Q Supabase Client
Handles all database logging for surgical telemetry, quantum integrity, and breach events.
"""

from supabase import create_client, Client
import threading

SUPABASE_URL = "https://kdtskvugdhtwjegdegno.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkdHNrdnVnZGh0d2plZ2RlZ25vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NzIxNTcsImV4cCI6MjA4ODM0ODE1N30.jBUXZ9iH35uw3XGMAE4Gi90BOFkXsO9YEsDSt4iRq48"

_client: Client = None
_lock = threading.Lock()

def get_client() -> Client:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def log_telemetry(force_applied: int, quantum_integrity: int,
                  latency_ms: int, joystick_x: int, joystick_y: int,
                  socket_active: bool, hw_active: bool,
                  breach_detected: bool = False):
    """
    Insert a telemetry snapshot into the 'telemetry_logs' table.
    Runs in a background thread so it never blocks the UI loop.
    """
    def _insert():
        try:
            client = get_client()
            client.table("telemetry_logs").insert({
                "force_applied": force_applied,
                "quantum_integrity": quantum_integrity,
                "latency_ms": latency_ms,
                "joystick_x": joystick_x,
                "joystick_y": joystick_y,
                "socket_active": socket_active,
                "hw_active": hw_active,
                "breach_detected": breach_detected,
            }).execute()
        except Exception as e:
            print(f"[Supabase] Log error: {e}")

    threading.Thread(target=_insert, daemon=True).start()


def log_robot_sync(fsr_value: int, joystick_cmd: int, hw_active: bool):
    """
    Insert a robot arm sync event into 'robot_sync_logs' table.
    """
    def _insert():
        try:
            client = get_client()
            client.table("robot_sync_logs").insert({
                "fsr_value": fsr_value,
                "joystick_cmd": joystick_cmd,
                "hw_active": hw_active,
            }).execute()
        except Exception as e:
            print(f"[Supabase] Robot log error: {e}")

    threading.Thread(target=_insert, daemon=True).start()


def log_breach_event(reason: str = "QUANTUM ENTANGLEMENT COLLAPSED"):
    """
    Insert a critical breach event into 'breach_events' table.
    """
    def _insert():
        try:
            client = get_client()
            client.table("breach_events").insert({
                "reason": reason,
                "severity": "CRITICAL",
            }).execute()
            print(f"[Supabase] Breach event logged: {reason}")
        except Exception as e:
            print(f"[Supabase] Breach log error: {e}")

    threading.Thread(target=_insert, daemon=True).start()
