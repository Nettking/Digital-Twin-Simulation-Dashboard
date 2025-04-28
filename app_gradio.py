# p_gradio.py

import gradio as gr
import pandas as pd
import time
import random

# ─── Mock sensor functions ────────────────────────────────────────────────────
def simulate_camera_capture():
    return {}

def simulate_vibration_sensor():
    return {"vibration": random.uniform(0, 20)}

def simulate_microphone_sensor():
    return {"sound_level": random.uniform(30, 120)}

def ingest_data(cam, vib, mic):
    return {
        "camera_event": cam,
        "vibration_event": vib,
        "microphone_event": mic
    }

# ─── Global session state ─────────────────────────────────────────────────────
state = {
    "timestamps": [],
    "vibration_data": [],
    "sound_data": [],
    "anomalies_log": [],
    "start_time": None,
    "is_running": False
}

# ─── Simulation step ──────────────────────────────────────────────────────────
def run_simulation_step(total_run_time, readings_per_second, vibration_threshold, sound_threshold):
    if not state["is_running"]:
        return gr.update(), gr.update(), gr.update(), gr.update()
    elapsed = time.time() - state["start_time"]
    if elapsed > total_run_time:
        state["is_running"] = False
        return "✅ Done", gr.update(), gr.update(), gr.update()

    ts = time.strftime("%H:%M:%S")
    vib = simulate_vibration_sensor()["vibration"]
    snd = simulate_microphone_sensor()["sound_level"]
    state["timestamps"].append(ts)
    state["vibration_data"].append(vib)
    state["sound_data"].append(snd)

    if vib > vibration_threshold:
        state["anomalies_log"].append(f"{ts} – High vibration: {vib:.2f} mm/s")
    if snd > sound_threshold:
        state["anomalies_log"].append(f"{ts} – High sound level: {snd:.2f} dB")

    latest_vib = f"{vib:.2f} mm/s"
    latest_snd = f"{snd:.2f} dB"

    df = pd.DataFrame({
        "Time": state["timestamps"],
        "Vibration (mm/s)": state["vibration_data"],
        "Sound Level (dB)": state["sound_data"]
    })
    df_long = df.melt(
        id_vars=["Time"],
        value_vars=["Vibration (mm/s)", "Sound Level (dB)"],
        var_name="Series",
        value_name="Value"
    )

    recent_anomalies = (
        "\n".join(state["anomalies_log"][-10:])
        if state["anomalies_log"] else
        "No anomalies detected yet."
    )

    return latest_vib, latest_snd, df_long, recent_anomalies

# ─── Start / Stop handlers ─────────────────────────────────────────────────────
def start_simulation():
    state["timestamps"].clear()
    state["vibration_data"].clear()
    state["sound_data"].clear()
    state["anomalies_log"].clear()
    state["start_time"] = time.time()
    state["is_running"] = True
    return gr.update(active=True), "▶️ Simulation Started"

def stop_simulation():
    state["is_running"] = False
    return gr.update(active=False), "⏹ Simulation Stopped"

# ─── Build Gradio UI ───────────────────────────────────────────────────────────
with gr.Blocks() as app:
    gr.Markdown("## Digital Twin Simulation Dashboard")

    with gr.Row():
        total_run_time      = gr.Number(label="Total run time (s)", value=30, precision=0)
        readings_per_second = gr.Number(label="Readings per second", value=2, precision=0)
        vibration_threshold = gr.Number(label="Vibration threshold (mm/s)", value=8.0)
        sound_threshold     = gr.Number(label="Sound threshold (dB)", value=85.0)

    with gr.Row():
        start_btn = gr.Button("▶️ Start Simulation")
        stop_btn  = gr.Button("⏹ Stop Simulation")
        status_tb = gr.Textbox(label="Status", interactive=False)

    with gr.Row():
        vib_tb = gr.Textbox(label="Latest Vibration", interactive=False)
        snd_tb = gr.Textbox(label="Latest Sound Level", interactive=False)

    line_plot   = gr.LinePlot(x="Time", y="Value", color="Series")
    anomaly_log = gr.Textbox(label="Recent Anomalies", lines=10, interactive=False)

    timer = gr.Timer(value=1.0, active=False)
    timer.tick(
        fn=run_simulation_step,
        inputs=[total_run_time, readings_per_second, vibration_threshold, sound_threshold],
        outputs=[vib_tb, snd_tb, line_plot, anomaly_log]
    )

    start_btn.click(fn=start_simulation, inputs=[], outputs=[timer, status_tb])
    stop_btn.click(fn=stop_simulation,  inputs=[], outputs=[timer, status_tb])

# ─── Enable queueing and launch with a public link ─────────────────────────────
app = app.queue()
app.launch(share=True)
