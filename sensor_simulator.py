import random
import time

def simulate_camera_capture():
    # Simulate a new image being captured
    return {"timestamp": time.time(), "image_captured": True}

def simulate_vibration_sensor():
    # Simulate a vibration value (e.g., in mm/s)
    vibration_value = random.uniform(0.0, 10.0)  # Normal range 0–10
    return {"timestamp": time.time(), "vibration": vibration_value}

def simulate_microphone_sensor():
    # Simulate microphone sound level (e.g., in decibels)
    sound_level = random.uniform(30.0, 90.0)  # Normal speech: 60 dB, loud noise: 80+
    return {"timestamp": time.time(), "sound_level": sound_level}
