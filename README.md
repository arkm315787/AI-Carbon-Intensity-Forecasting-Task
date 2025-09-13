# AI Carbon Intensity Forecasting & API Service

This project is part of the **Zerofy AI Carbon Intensity Coding Task**. It includes:

- **XGBoost model** to forecast carbon intensity for the next 24 hours.
- A **Flask API** with MongoDB backend to serve and retrieve forecasts.

---

## Forecasting Model

### Model Type
- **XGBoost Regressor** using:
  - Lag features: `lag1`, `lag2`, `lag24`
  - Time-based features: `hour`, `day of week`, `is_weekend`
  - Sine/cosine encoding of hour
  - Rolling mean (`roll24`)

### Forecast Horizon
- Predicts **next 24 hours** carbon intensity (gCO₂/kWh) based on latest known data.

### Accuracy Metrics
| Dataset | Method         | MAE     | RMSE    |
|---------|----------------|---------|---------|
| Val     | Baseline-24h   | 52.56  | 69.56  |
| Val     | XGBoost (best) | 13.63  | 20.11  |
| Test    | Baseline-24h   | 83.17  | 108.11 |
| Test    | XGBoost (final)| 13.81  | 19.44  |
| Test    | MINN (final)   | 19.95  | 26.31  |

---


## API Service

The model is deployed using a **Flask app** with **MongoDB backend**.

### Endpoints

#### `POST /forecast`
- Runs the forecasting model
- Stores the next 24 hours in MongoDB
- One document per day (`yyyy-mm-dd` format)

#### `GET /forecast/:date`
- Fetches the forecast for a given date
- If the forecast exists, returns 24 hourly values
- Otherwise, returns an empty array

---

## MongoDB Structure

Database: `task1_forecasting`  
Collection: `forecasts`

Each document:
```json
{
  "date": "2025-07-01",
  "values": [511.47, 510.89, ..., 455.78]
}
```

---


## 🚀 How to Run

1. Clone the repo:
```bash
git clone https://github.com/arkm315787/ai-carbon-intensity.git
cd ai-carbon-intensity
```
---

2. Install Dependencies

```bash
pip install -r requirements.txt
```
---

3. Start the web server:

```bash
python app.py
```
---

4. Test endpoints:

```bash
curl -X POST http://127.0.0.1:5000/forecast
curl http://127.0.0.1:5000/forecast/YYYY-MM-DD
```
---

Or use Python

```bash
import requests
requests.post("http://127.0.0.1:5000/forecast")
requests.get("http://127.0.0.1:5000/forecast/2025-07-01")
```
---

