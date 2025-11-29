# predictor/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
from dotenv import load_dotenv

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "models/hospital_model.pkl")
model = joblib.load(MODEL_PATH)

app = FastAPI()

class PredictRequest(BaseModel):
    aqi: int
    temp: float
    season: int = 0
    viral_cases: int = 0
    festival_flag: int = 0

@app.post("/predict")
def predict(req: PredictRequest):
    features = [[req.aqi, req.temp, req.season, req.viral_cases, req.festival_flag]]
    pred = model.predict(features)[0]
    # return rounded + risk level
    pred_int = int(max(0, round(pred)))
    risk = "low"
    if pred_int > 120:
        risk = "high"
    elif pred_int > 80:
        risk = "medium"
    return {"predicted_load": pred_int, "risk_level": risk}
