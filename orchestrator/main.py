# orchestrator/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()
FETCH_URL = os.getenv("FETCH_URL", "http://localhost:8001/fetch")
PRED_URL  = os.getenv("PRED_URL", "http://localhost:8002/predict")
REC_URL   = os.getenv("REC_URL", "http://localhost:8003/recommend")

app = FastAPI()

class OrchestrateRequest(BaseModel):
    city: str
    date: str = None
    hospital_id: str = None

@app.post("/run")
def run(req: OrchestrateRequest):
    # 1) Fetch
    r = requests.post(FETCH_URL, json={"city": req.city, "date": req.date}, timeout=8)
    if not r.ok:
        return {"error": "fetch failed", "detail": r.text}
    fetch_out = r.json()

    # 2) Predict
    pred_in = {
        "aqi": fetch_out["aqi"],
        "temp": fetch_out["temp"],
        "season": (fetch_out["date"] and int(fetch_out["date"].split("-")[1])%12//3) or 0,
        "viral_cases": fetch_out.get("viral_cases", 0),
        "festival_flag": fetch_out.get("festival_flag", 0)
    }
    r2 = requests.post(PRED_URL, json=pred_in, timeout=8)
    if not r2.ok:
        return {"error": "predict failed", "detail": r2.text}
    pred_out = r2.json()

    # 3) Recommend
    rec_in = {
        "predicted_load": pred_out["predicted_load"],
        "risk_level": pred_out["risk_level"],
        "aqi": fetch_out["aqi"],
        "temp": fetch_out["temp"],
        "festival_flag": fetch_out["festival_flag"]
    }
    r3 = requests.post(REC_URL, json=rec_in, timeout=8)
    if not r3.ok:
        return {"error": "recommend failed", "detail": r3.text}
    rec_out = r3.json()

    # Compose final response
    return {
        "fetch": fetch_out,
        "predict": pred_out,
        "recommendation": rec_out
    }
