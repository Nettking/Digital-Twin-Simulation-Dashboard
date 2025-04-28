import time
from sensor_simulator import simulate_camera_capture, simulate_vibration_sensor, simulate_microphone_sensor
from data_ingestion import ingest_data
from anomaly_detection import detect_anomalies

def main_loop(cycles=10, delay=1):
    print("Starting Digital Twin Simulation...")
    
    for _ in range(cycles):
        # Simulate each sensor
        camera_data = simulate_camera_capture()
        vibration_data = simulate_vibration_sensor()
        microphone_data = simulate_microphone_sensor()
        
        # Ingest the data
        event = ingest_data(camera_data, vibration_data, microphone_data)
        
        # Detect anomalies
        anomalies = detect_anomalies(event)
        
        # Print results
        print(f"Event at {time.ctime(event['camera_event']['timestamp'])}:")
        print(f"  Vibration: {event['vibration_event']['vibration']:.2f} mm/s")
        print(f"  Sound Level: {event['microphone_event']['sound_level']:.2f} dB")
        if anomalies:
            print("  Anomalies Detected:")
            for anomaly in anomalies:
                print(f"   - {anomaly}")
        else:
            print("  No anomalies detected.")
        
        print("-" * 50)
        time.sleep(delay)

if __name__ == "__main__":
    main_loop()
