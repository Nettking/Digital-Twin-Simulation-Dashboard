# Digital Twin Simulation Dashboard

A **Streamlit**-based application that simulates real-time sensor data (camera events, vibration, microphone), performs threshold-based anomaly detection, and offers optional machine-learning (IsolationForest) anomaly detection. Fully configurable via sidebar controls and containerized via Docker for straightforward deployment.

## Features

- **Real-time sensor simulation** of:  
  - Camera capture events  
  - Vibration readings  
  - Microphone sound levels  
- **Threshold-based anomaly detection**: configurable thresholds trigger alerts in the dashboard  
- **ML-based anomaly detection**: use IsolationForest to flag outliers after a simulation run  
- **Configurable parameters** via Streamlit sidebar:  
  - Total run time & readings per second  
  - Vibration & sound thresholds  
  - Batch size (manual simulation mode)  
- **Dockerized** for zero-install deployment  

## Project Structure
- `app.py`                  – Main Streamlit dashboard  
- `sensor_simulator.py`     – Fake data generators for camera, vibration, mic  
- `data_ingestion.py`       – Combines sensor outputs into events  
- `anomaly_detection.py`    – Threshold-based detection logic  
- `requirements.txt`        – Python dependencies  
- `Dockerfile`              – Container setup for Streamlit app  
- `README.md`               – This file  

## Prerequisites

- **Python 3.10+**  
- **pip**  
- (Optional) **Docker** for containerized run  

## Local Installation & Usage

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/dt-simulation-dashboard.git
   cd dt-simulation-dashboard
  ```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the app**
```bash
streamlit run app.py
```

4. **Open your browser** at 
```bash
http://localhost:8501
```
## Docker Deployment
1. **Build the Docker image**
```bash
docker build -t dt-dashboard .
```
2. **Run the container**
```bash
docker run -p 8501:8501 dt-dashboard
```
3. **Browse to** 
```bash
http://localhost:8501
```
## License
This project is released under the MIT License. Feel free to use and modify as you see fit.
