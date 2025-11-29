"""Predictor Agent - Combines data from all agents to forecast hospital load."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from datetime import datetime

from nest import Agent, tool
from utils.model_helpers import (
    predict_opd_load,
    predict_emergency_load,
    predict_icu_load,
)


BASE_LOADS = {
    "Mumbai": {"opd": 450, "emergency": 120, "icu": 60},
    "Delhi": {"opd": 500, "emergency": 150, "icu": 70},
    "Bangalore": {"opd": 400, "emergency": 110, "icu": 55},
    "Kolkata": {"opd": 420, "emergency": 115, "icu": 50},
    "Chennai": {"opd": 380, "emergency": 90, "icu": 45},
    "Hyderabad": {"opd": 360, "emergency": 95, "icu": 48},
    "Pune": {"opd": 320, "emergency": 80, "icu": 40},
}


def _get_base_load(city: str) -> Dict[str, int]:
    """Return base load numbers for the city or defaults."""
    return BASE_LOADS.get(city, {"opd": 350, "emergency": 100, "icu": 45})


@tool
def predict_hospital_load(
    data_bundle: Dict[str, Any],
    pollution_output: Dict[str, Any],
    festival_output: Dict[str, Any],
    disease_output: Dict[str, Any],
) -> Dict[str, Any]:
    """Combine agent outputs and predict hospital resource loads."""
    city = data_bundle.get("city", "Mumbai")
    base = _get_base_load(city)

    pollution = pollution_output.get("pollution_impact", {})
    festival = festival_output.get("festival_impact", {})
    disease = disease_output.get("disease_impact", {})

    factors = {
        "aqi": data_bundle.get("pollution", {}).get("aqi", 80),
        "festival_score": festival.get("severity_score", 0),
        "disease_score": disease.get("severity_score", 0),
        "temperature": data_bundle.get("weather", {}).get("temperature", 30),
    }

    loads = {
        "opd": predict_opd_load(base["opd"], factors),
        "emergency": predict_emergency_load(base["emergency"], factors),
        "icu": predict_icu_load(base["icu"], factors),
    }
    loads["ventilator"] = max(5, int(loads["icu"] * 0.35))
    loads["pharmacy"] = int(loads["opd"] * 1.2)

    # Combined severity considers surges from pollution/festival/disease
    combined_severity = min(
        1.0,
        (
            pollution.get("severity_score", 0)
            + festival.get("severity_score", 0)
            + disease.get("severity_score", 0)
        )
        / 2.5,
    )

    # Provide qualitative risk
    if combined_severity >= 0.75:
        risk = "Critical"
    elif combined_severity >= 0.5:
        risk = "High"
    elif combined_severity >= 0.3:
        risk = "Moderate"
    else:
        risk = "Low"

    return {
        "city": city,
        "date": data_bundle.get("date"),
        "loads": loads,
        "risk_level": risk,
        "combined_severity": round(combined_severity, 3),
        "drivers": {
            "pollution": pollution,
            "festival": festival,
            "disease": disease,
        },
        "confidence": _estimate_confidence(data_bundle, pollution, festival, disease),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def _estimate_confidence(
    data_bundle: Dict[str, Any],
    pollution: Dict[str, Any],
    festival: Dict[str, Any],
    disease: Dict[str, Any],
) -> float:
    """Simple heuristic for confidence score."""
    score = 0.5
    if data_bundle.get("pollution", {}).get("source") == "open-meteo":
        score += 0.1
    if data_bundle.get("weather", {}).get("source") == "open-meteo":
        score += 0.05
    if festival.get("festival_name"):
        score += 0.05
    if disease.get("severity_score", 0) > 0.4:
        score += 0.05
    return round(min(0.95, score), 3)


predictor_agent = Agent(
    name="PredictorAgent",
    instructions=(
        "Combines outputs from data, pollution, festival, and disease agents to "
        "predict OPD, emergency, ICU, ventilator, and pharmacy loads."
    ),
    tools=[predict_hospital_load],
)

if __name__ == "__main__":
    from nest import run

    run(predictor_agent, port=8014)

