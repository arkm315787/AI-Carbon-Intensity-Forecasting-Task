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
| Val     | XGBoost (best) | 13.49  | 19.96  |
| Test    | Baseline-24h   | 83.17  | 108.11 |
| Test    | XGBoost (final)| 13.82  | 19.53  |
| Test    | MINN (final)   | 16.51  | 22.51  |

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

## Discussion & Conclusions

**What makes this easy or hard?**

- **Easy:**
- High persistence: strong autocorrelation → lag1 dominates feature importance (one-step-ahead uses the last hour you already know).
- Small, clean dataset (~4.3k hours) and one target signal → fast training/inference on CPU (both XGBoost and MINN).

- **Hard:**
- Ramps & peaks: sharp spikes (seen in residual time plot and parity scatter’s upper tail) are poorly predicted without external drivers.
- Multi-month trend, and holiday effects can shift the baseline abruptly.
- Univariate limitation: with only y, models must infer weather & generation mix indirectly; limited ability to anticipate sudden changes.
---

**What could make results more accurate?**  

- Add exogenous drivers (see next section): wind/solar forecasts, load, generation mix, imports/exports, temperature, prices.
- Direct multi-horizon training for day-ahead: so each hour h uses only history up to time t, not earlier predictions → avoids error compounding and      captures horizon-specific behavior (e.g., evening peaks).
- Weekly memory & robust features: include lag168, roll168, rolling std/volatility, holiday flags.
- **Better loss/objective for peaks**: Standard loss functions like MSE or RMSE treat all errors equally, whether you underpredict a low value (e.g.,   120 gCO₂/kWh) or a high one (e.g., 520 gCO₂/kWh). But high carbon intensity hours are more critical operationally as they contribute more to     emissions and policy violations. So weighted RMSE or quantile (pinball) loss can be used to emphasize high carbon intensity hours that matter operationally.
- Ensembles: blend baseline (t-24), XGB, and a small NN; per-horizon ensembling often improves stability.
- Proper backtesting: sliding-window cross-validation across weeks to pick hyperparameters that generalize.
  like: Week 1–3 → train  
        Week 4   → validation  
        Week 5–7 → train  
        Week 8   → validation
---

**What other methods would you consider if this were production?**  

- LightGBM / XGBoost: Gradient-boosted decision trees scale well with exogenous variables (e.g., weather, demand, generation mix) and provide strong performance with relatively low tuning effort.
- **Neural Networks (when exogenous & temporal data are rich):**
- N-BEATS: Deep backcast-forecast models that perform well in time series benchmarks, especially for deterministic multi-horizon forecasting.
- TFT (Temporal Fusion Transformer): Powerful for multi-horizon prediction when many covariates are involved, combining attention, gating, and quantile loss.
- **Probabilistic Forecasting (crucial for operational decision-making):**

In real-world operations, point forecasts are not enough; therefore, grid operators, markets, and optimizers need uncertainty quantification to make risk-aware decisions.
- Quantile Regression: Produces multiple percentiles (P10, P50, P90), giving a range of likely outcomes.
NGBoost: A gradient boosting framework that directly models predictive distributions, not just mean values.
- Deep Probabilistic Models (TFT with quantile loss): Provide full forecast distributions, enabling scenario-based dispatching, confidence bands for CI, and robust reserve scheduling.

---



**Other methods to consider in production:**  
- LightGBM/CatBoost with exogenous features; linear ridge/Lasso per horizon; SARIMAX as transparent baseline; TFT/TCN/N-BEATS/NHITS with drivers; simple model stacking.

**Key drivers of carbon intensity:**  
- Generation mix (renewables vs fossil), demand level/ramps, weather, imports/exports, fuel prices.

**Sources of inaccuracy:**  
- Errors in exogenous forecasts, unmodelled events (outages/maintenance), holidays & DST transitions, regime changes.

---

**Q1. How do you evaluate forecast accuracy?**

- I evaluated forecast accuracy using two standard metrics:

- Mean Absolute Error (MAE): to measure average deviation in a human-readable unit (gCO₂/kWh).

- Root Mean Squared Error (RMSE): to penalize larger errors more heavily and assess model robustness.

These were computed for both:

- A validation set (for model tuning)

- A test set (to evaluate generalization on unseen data)

I also included a simple naïve baseline (24h lag) for both sets to benchmark model performance

---

**Q2. What worked well?**

- Recursive XGBoost modeling: performed well with limited data, handled temporal lags efficiently.

- Feature engineering: Adding lag1, lag24, hour of day, weekend flags, and sine/cosine time encodings significantly improved the forecast.

- Baseline comparison: helped verify that our model meaningfully outperforms a simple persistence model.

- API integration: worked smoothly with Flask and MongoDB, making the model deployable in real-world scenarios.

---

**Q3. What didn’t work well?**

- Longer lags (e.g., lag 48+) and complex derived features introduced instability and noise due to limited training data.

- MINN (deep model): performed slightly worse than XGBoost on the test set — likely due to overfitting on a relatively small dataset and lack of exogenous features.

---

**Q5. What are the key drivers of carbon intensity in electricity grids?**

Key drivers include:

- Generation mix (how much energy comes from coal, gas, nuclear, wind, solar, hydro)

- Demand peaks: high demand often triggers fossil fuel-based backup power

- Weather conditions: solar/wind variability affects renewable generation

- Grid imports/exports: carbon intensity depends on neighboring countries' supply

- Policy and fuel availability: carbon prices and resource constraints also shape intensity trends
