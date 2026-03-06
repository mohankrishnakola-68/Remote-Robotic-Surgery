-- =====================================================
-- Haptic-Q: QSDC Surgical System — Supabase Schema
-- Run this SQL once in: Supabase → SQL Editor → New Query
-- =====================================================

-- 1. Telemetry Logs (from Surgeon Console)
CREATE TABLE IF NOT EXISTS telemetry_logs (
    id                BIGSERIAL PRIMARY KEY,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    force_applied     INTEGER NOT NULL DEFAULT 0,        -- 0–255 mN
    quantum_integrity INTEGER NOT NULL DEFAULT 100,      -- 0–100 %
    latency_ms        INTEGER NOT NULL DEFAULT 0,        -- round-trip ms
    joystick_x        INTEGER NOT NULL DEFAULT 128,      -- 0–255
    joystick_y        INTEGER NOT NULL DEFAULT 128,      -- 0–255
    socket_active     BOOLEAN NOT NULL DEFAULT FALSE,
    hw_active         BOOLEAN NOT NULL DEFAULT FALSE,
    breach_detected   BOOLEAN NOT NULL DEFAULT FALSE
);

-- 2. Robot Arm Sync Logs (from feedback_sync.py)
CREATE TABLE IF NOT EXISTS robot_sync_logs (
    id            BIGSERIAL PRIMARY KEY,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    fsr_value     INTEGER NOT NULL DEFAULT 0,    -- Force-Sensitive Resistor reading
    joystick_cmd  INTEGER NOT NULL DEFAULT 128,  -- Command sent back to robot
    hw_active     BOOLEAN NOT NULL DEFAULT FALSE
);

-- 3. Breach Events (Critical Security Log)
CREATE TABLE IF NOT EXISTS breach_events (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reason     TEXT NOT NULL DEFAULT 'UNKNOWN',
    severity   TEXT NOT NULL DEFAULT 'CRITICAL'
);

-- =====================================================
-- Enable Row Level Security (RLS) — allow anon inserts
-- =====================================================

ALTER TABLE telemetry_logs  ENABLE ROW LEVEL SECURITY;
ALTER TABLE robot_sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE breach_events   ENABLE ROW LEVEL SECURITY;

-- Policy: allow anon role to insert (the Python client uses anon key)
CREATE POLICY "Allow anon insert telemetry"
    ON telemetry_logs FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anon insert robot_sync"
    ON robot_sync_logs FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anon insert breach"
    ON breach_events FOR INSERT TO anon WITH CHECK (true);

-- Policy: allow anon role to read (for the dashboard)
CREATE POLICY "Allow anon select telemetry"
    ON telemetry_logs FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anon select robot_sync"
    ON robot_sync_logs FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anon select breach"
    ON breach_events FOR SELECT TO anon USING (true);

-- Done! Run the full console + robot arm system.
-- Data will appear in these tables in real-time.
