def detect_anomalies(event):
    anomalies = []
    
    # Check vibration threshold
    vibration_value = event["vibration_event"]["vibration"]
    if vibration_value > 8.0:
        anomalies.append(f"High vibration detected: {vibration_value:.2f} mm/s")
    
    # Check sound level threshold
    sound_level = event["microphone_event"]["sound_level"]
    if sound_level > 85.0:
        anomalies.append(f"High sound level detected: {sound_level:.2f} dB")
    
    return anomalies
