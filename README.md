# ChilliRover Intelligence System — Flask Dashboard
**Project R26-IT-075 · SLIIT · Dept. of Information Technology**

Smart Chilli Crop Intelligence System Using an Autonomous Ground Rover

---

## Components Covered

| # | Component | Model | Data Source |
|---|-----------|-------|-------------|
| C1 | Soil Moisture Anomaly Detection | Random Forest + Isolation Forest | CAF Sensor Network |
| C2 | Chilli Disease Detection | EfficientNetB0 | Camera (Kaggle dataset) |
| C3 | Field Zone Mapping | K-Means Clustering | Sentinel-2 Multispectral |
| C4 | Soil Health Detection | LSTM + XGBoost | NPK Sensor Dataset |

---

## Setup

### 1. Prerequisites
- Python 3.9+
- MongoDB running locally on port 27017
- DB name: `chilli` (auto-created)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run
```bash
python app.py
```
Navigate to: http://localhost:5000

### 4. Default Login
- **Username:** `admin`
- **Password:** `admin123`

---

## MongoDB Collections (auto-seeded on first run)

| Collection | Purpose |
|---|---|
| `users` | Authenticated system users |
| `sensor_logs` | Soil moisture sensor readings + anomaly flags |
| `disease_logs` | Disease classification results |
| `field_zones` | K-Means cluster zone summaries |
| `soil_health` | NPK-based soil health predictions |

---

## Project Structure

```
chilli_app/
├── app.py                  # Flask application + routes
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout (sidebar, topbar)
│   ├── login.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   └── users.html          # User management
└── static/
    ├── css/main.css
    └── js/main.js
```
