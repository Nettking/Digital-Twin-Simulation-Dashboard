def ingest_data(camera_data, vibration_data, microphone_data):
    # Combine all sensor inputs into a single event
    event = {
        "camera_event": camera_data,
        "vibration_event": vibration_data,
        "microphone_event": microphone_data,
    }
    return event
