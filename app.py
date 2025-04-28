import streamlit as st
import pandas as pd
import time

from streamlit_autorefresh import st_autorefresh
from sensor_simulator     import simulate_camera_capture, simulate_vibration_sensor, simulate_microphone_sensor
from data_ingestion       import ingest_data

# ─── 1) Page config must be first ─────────────────────────────────────────────
st.set_page_config(page_title="DT Simulation Dashboard", layout="wide")

# ─── 2) Header ─────────────────────────────────────────────────────────────────
st.title("Digital Twin Simulation Dashboard")
st.subheader("Real-time sensor data for a set duration")

# ─── 3) Sidebar settings ───────────────────────────────────────────────────────
st.sidebar.header("Simulation Settings")
total_run_time      = st.sidebar.number_input("Total run time (s)",        min_value=1, max_value=600, value=30, step=1)
readings_per_second = st.sidebar.number_input("Readings per second",       min_value=1, max_value=20,  value=2,  step=1)
vibration_threshold = st.sidebar.number_input("Vibration threshold (mm/s)",min_value=0.1, max_value=100.0, value=8.0, step=0.1)
sound_threshold     = st.sidebar.number_input("Sound threshold (dB)",      min_value=0.1, max_value=200.0, value=85.0, step=0.1)

# ─── 4) Session state defaults ─────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("is_running",     False)
ss.setdefault("start_time",     0.0)
ss.setdefault("timestamps",     [])
ss.setdefault("vibration_data", [])
ss.setdefault("sound_data",     [])
ss.setdefault("anomalies_log",  [])

# ─── 5) Control buttons ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Simulation"):
        ss.is_running     = True
        ss.start_time     = time.time()
        ss.timestamps[:]  = []
        ss.vibration_data[:] = []
        ss.sound_data[:]  = []
        ss.anomalies_log[:] = []
with col2:
    if st.button("⏹ Stop Simulation"):
        ss.is_running = False

# ─── 6) Only auto-refresh when running ─────────────────────────────────────────
if ss.is_running:
    # trigger a rerun every 1 second
    st_autorefresh(interval=1000, limit=None, key="autorefresh")

    # run simulation logic each rerun
    elapsed = time.time() - ss.start_time
    if elapsed <= total_run_time:
        # how many new readings we *should* have so far
        expected = int(elapsed * readings_per_second)
        have     = len(ss.timestamps)
        to_gen   = expected - have

        for _ in range(to_gen):
            cam = simulate_camera_capture()
            vib = simulate_vibration_sensor()
            mic = simulate_microphone_sensor()
            event = ingest_data(cam, vib, mic)

            ts = time.strftime("%H:%M:%S")
            ss.timestamps.append(ts)
            ss.vibration_data.append(event["vibration_event"]["vibration"])
            ss.sound_data.append(event["microphone_event"]["sound_level"])

            if event["vibration_event"]["vibration"] > vibration_threshold:
                ss.anomalies_log.append(f"{ts} – High vibration: {event['vibration_event']['vibration']:.2f} mm/s")
            if event["microphone_event"]["sound_level"] > sound_threshold:
                ss.anomalies_log.append(f"{ts} – High sound level: {event['microphone_event']['sound_level']:.2f} dB")
    else:
        ss.is_running = False
        st.success("✅ Simulation complete")

# ─── 7) Dashboard display (always visible) ────────────────────────────────────
if ss.timestamps:
    m1, m2 = st.columns(2)
    m1.metric("Latest Vibration",   f"{ss.vibration_data[-1]:.2f} mm/s")
    m2.metric("Latest Sound Level", f"{ss.sound_data[-1]:.2f} dB")

    df = pd.DataFrame({
        "Time":              ss.timestamps,
        "Vibration (mm/s)":  ss.vibration_data,
        "Sound Level (dB)":  ss.sound_data
    })
    st.line_chart(df.set_index("Time"))

    st.markdown("### Recent Anomalies")
    if ss.anomalies_log:
        for entry in ss.anomalies_log[-10:]:
            st.error(entry)
    else:
        st.success("No anomalies detected yet.")
