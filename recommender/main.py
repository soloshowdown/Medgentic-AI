# recommender/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")  # optional

app = FastAPI()

class RecRequest(BaseModel):
    predicted_load: int
    risk_level: str
    aqi: int
    temp: float
    festival_flag: int

def rule_based_recommendation(predicted_load, risk, aqi, festival_flag):
    # baseline staffing: 50 staff per 100 patients (example)
    base_staff = max(5, int(predicted_load * 0.5 / 10)) * 10
    if risk == "high":
        staff_needed = int(base_staff * 1.5)
    elif risk == "medium":
        staff_needed = int(base_staff * 1.2)
    else:
        staff_needed = base_staff

    # supply calculation
    masks = int(predicted_load * (0.7 if aqi > 100 else 0.3))
    oxygen_cylinders = max(0, int(predicted_load * 0.02))
    extra_beds = max(0, predicted_load - 100)

    actions = {
        "staffing": f"Arrange approximately {staff_needed} staff (doctors+nurses+support).",
        "supplies": f"Stock N95 masks: {masks}, Oxygen cylinders: {oxygen_cylinders}, Basic meds.",
        "beds": f"Reserve/prepare {extra_beds} extra beds/observation chairs.",
        "alerts": "Notify emergency department & on-call staff.",
        "notes": "If festival_flag=1, expect non-respiratory surges (injuries)."
    }
    return actions

@app.post("/recommend")
def recommend(req: RecRequest):
    # If OpenAI key present, you can call it here with a prompt (not included to keep this self-contained)
    # Fallback to rule-based
    rec = rule_based_recommendation(req.predicted_load, req.risk_level, req.aqi, req.festival_flag)
    rec["explanation"] = f"Predicted load {req.predicted_load}, risk {req.risk_level}, AQI {req.aqi}"
    return rec
