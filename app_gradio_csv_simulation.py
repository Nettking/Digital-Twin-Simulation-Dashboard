import gradio as gr
import pandas as pd
import time

# ─── Global session state ─────────────────────────────────────────────────────
state = {
    "df": None,
    "start_time": None,
    "is_running": False,
    "idx": 0,
    "timestamps": [],
    "vibration_data": [],
    "sound_data": [],
    "anomalies_log": [],
}

# ─── 1) Load CSV and set slider range ──────────────────────────────────────────
def load_csv(csv_file):
    df = pd.read_csv(csv_file.name)
    # Ensure required columns exist
    for col in ["Time", "Vibration (mm/s)", "Sound Level (dB)"]:
        if col not in df.columns:
            raise gr.Error(f"CSV must contain column '{col}'")
    state["df"] = df.reset_index(drop=True)
    max_time = int(df["Time"].max())
    # Reset any previous simulation state
    state.update({
        "start_time": None, "is_running": False, "idx": 0,
        "timestamps": [], "vibration_data": [], "sound_data": [], "anomalies_log": []
    })
    return (
        gr.update(maximum=max_time, value=0),
        "✅ CSV loaded, max time = {} s".format(max_time)
    )

# ─── 2) Simulation step ──────────────────────────────────────────────────────────
def run_simulation_step(run_time, vibration_threshold, sound_threshold):
    # If no file or not running, no-op
    if state["df"] is None or not state["is_running"]:
        return gr.update(), gr.update(), gr.update(), gr.update()

    elapsed = time.time() - state["start_time"]
    idx = int(elapsed)
    df = state["df"]

    # Stop if we've reached either the selected run_time or end of file
    if idx > run_time or idx >= len(df):
        state["is_running"] = False
        return "✅ Done", gr.update(), gr.update(), gr.update()

    # Only process a new row once
    if idx == state["idx"]:
        row = df.iloc[idx]
        ts  = row["Time"]
        vib = row["Vibration (mm/s)"]
        snd = row["Sound Level (dB)"]

        state["timestamps"].append(ts)
        state["vibration_data"].append(vib)
        state["sound_data"].append(snd)

        if vib > vibration_threshold:
            state["anomalies_log"].append(f"{ts} – High vibration: {vib:.2f} mm/s")
        if snd > sound_threshold:
            state["anomalies_log"].append(f"{ts} – High sound: {snd:.2f} dB")

        state["idx"] += 1

    latest_vib = f"{state['vibration_data'][-1]:.2f} mm/s"
    latest_snd = f"{state['sound_data'][-1]:.2f} dB"

    # Melt for dual-line plotting
    df_plot = pd.DataFrame({
        "Time": state["timestamps"],
        "Vibration (mm/s)": state["vibration_data"],
        "Sound Level (dB)": state["sound_data"]
    }).melt(
        id_vars=["Time"], var_name="Series", value_name="Value"
    )

    recent_anomalies = (
        "\n".join(state["anomalies_log"][-10:])
        if state["anomalies_log"] else "No anomalies detected yet."
    )

    return latest_vib, latest_snd, df_plot, recent_anomalies

# ─── 3) Start & Stop handlers ────────────────────────────────────────────────────
def start_simulation():
    if state["df"] is None:
        return gr.update(active=False), "⚠️ Upload a CSV first"
    state.update({
        "start_time": time.time(),
        "is_running": True,
        "idx": 0,
        "timestamps": [], "vibration_data": [], "sound_data": [], "anomalies_log": []
    })
    return gr.update(active=True), "▶️ Simulation Started"

def stop_simulation():
    state["is_running"] = False
    return gr.update(active=False), "⏹ Simulation Stopped"

# ─── 4) Build Gradio UI ───────────────────────────────────────────────────────────
with gr.Blocks() as app:
    gr.Markdown("## CSV-Driven Digital Twin Simulation")

    with gr.Row():
        csv_file = gr.File(label="Upload CSV", file_types=[".csv"])
        run_time  = gr.Slider(label="Playback duration (s)", minimum=0, maximum=1, step=1, value=0)
        vib_thresh = gr.Number(label="Vibration threshold (mm/s)", value=8.0)
        snd_thresh = gr.Number(label="Sound threshold (dB)",      value=85.0)

    with gr.Row():
        load_btn = gr.Button("📂 Load CSV")
        start_btn = gr.Button("▶️ Start")
        stop_btn  = gr.Button("⏹ Stop")
        status_tb = gr.Textbox(label="Status", interactive=False)

    with gr.Row():
        vib_tb = gr.Textbox(label="Latest Vibration", interactive=False)
        snd_tb = gr.Textbox(label="Latest Sound Level", interactive=False)

    line_plot   = gr.LinePlot(x="Time", y="Value", color="Series")
    anomaly_log = gr.Textbox(label="Recent Anomalies", lines=10, interactive=False)

    # Hidden timer, ticks once per second
    timer = gr.Timer(value=1.0, active=False)

    # Events
    load_btn.click(
        fn=load_csv,
        inputs=[csv_file],
        outputs=[run_time, status_tb]
    )

    timer.tick(
        fn=run_simulation_step,
        inputs=[run_time, vib_thresh, snd_thresh],
        outputs=[vib_tb, snd_tb, line_plot, anomaly_log]
    )

    start_btn.click(fn=start_simulation, inputs=[], outputs=[timer, status_tb])
    stop_btn.click(fn=stop_simulation,  inputs=[], outputs=[timer, status_tb])

# ─── 5) Enable queueing & launch ─────────────────────────────────────────────────
app = app.queue()
app.launch(share=True)
