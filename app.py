from flask import Flask, request, jsonify
import pandas as pd
from pymongo import MongoClient
from xgboost import XGBRegressor
import pickle

from forecast_utils import generate_forecast

app = Flask(__name__)

# Load model and data
model = pickle.load(open("model.pkl", "rb"))
df = pd.read_csv("data/engineered.csv", index_col=0, parse_dates=True)
X_cols = [c for c in df.columns if c != "y"]

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Task1_Forecasting"]
collection = db["forecast"]

# POST endpoint (already working)
@app.route("/forecast", methods=["POST"])
def forecast():
    result = generate_forecast(model, df, X_cols)

    # Upsert forecast to MongoDB
    for day_forecast in result:
        collection.update_one(
            {"date": day_forecast["date"]},
            {"$set": {"values": day_forecast["values"]}},
            upsert=True
        )

    return jsonify({"status": "success", "message": "Forecast saved", "data": result})


# NEW: GET endpoint to retrieve forecast by date
@app.route("/forecast/<date>", methods=["GET"])
def get_forecast(date):
    document = collection.find_one({"date": date})
    if document:
        return jsonify(document["values"])
    else:
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)
