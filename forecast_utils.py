# forecast_utils.py
import numpy as np
import pandas as pd

def generate_forecast(model, df_full, X_cols):
    state = df_full.copy()
    future_vals = []
    future_times = []

    for step in range(24):
        next_idx = state.index[-1] + pd.Timedelta(hours=1)
        row = {}

        if 'hour' in X_cols:        row['hour'] = next_idx.hour
        if 'dow' in X_cols:         row['dow'] = next_idx.dayofweek
        if 'is_weekend' in X_cols:  row['is_weekend'] = 1 if row['dow'] >= 5 else 0
        if 'sin_h' in X_cols:       row['sin_h'] = np.sin(2*np.pi*next_idx.hour/24)
        if 'cos_h' in X_cols:       row['cos_h'] = np.cos(2*np.pi*next_idx.hour/24)

        if 'lag1' in X_cols:        row['lag1'] = state['y'].iloc[-1]
        if 'lag2' in X_cols:        row['lag2'] = state['y'].iloc[-2]
        if 'lag24' in X_cols:       row['lag24'] = state['y'].iloc[-24]
        if 'roll24' in X_cols:      row['roll24'] = state['y'].iloc[-24:].mean()

        x_next = pd.DataFrame([row], index=[next_idx])[X_cols]
        yhat = float(model.predict(x_next))

        future_vals.append(yhat)
        future_times.append(next_idx)

        row['y'] = yhat
        state = pd.concat([state, pd.DataFrame([row], index=[next_idx])], sort=False)

    forecast_df = pd.Series(future_vals, index=pd.DatetimeIndex(future_times), name='forecast_24h')

    grouped = forecast_df.groupby(forecast_df.index.date)
    forecasts = []
    for date, series in grouped:
        hour_values = [round(v, 2) for v in series.values]
        forecasts.append({
            "date": str(date),
            "values": hour_values
        })

    return forecasts
