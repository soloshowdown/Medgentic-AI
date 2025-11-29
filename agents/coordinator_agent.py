"""Coordinator Agent - Orchestrates the full prediction pipeline."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from datetime import datetime

from nest import Agent, tool

from agents.data_agent import collect_all_data
from agents.pollution_agent import predict_pollution_impact
from agents.festival_agent import predict_festival_impact
from agents.disease_agent import analyze_disease_season
from agents.predictor_agent import predict_hospital_load
from agents.ops_agent import generate_resource_plan


@tool
def run_prediction_pipeline(city: str, date: str) -> Dict[str, Any]:
    """Run the full multi-agent pipeline and return consolidated prediction."""
    data_payload = collect_all_data(city=city, date=date)
    pollution_output = predict_pollution_impact(data_payload.get("pollution", {}))
    festival_output = predict_festival_impact(
        festivals=data_payload.get("festivals", []), date=date
    )
    disease_output = analyze_disease_season(
        health_data=data_payload.get("health", {}), date=date
    )
    predictor_output = predict_hospital_load(
        data_bundle=data_payload,
        pollution_output=pollution_output,
        festival_output=festival_output,
        disease_output=disease_output,
    )
    ops_output = generate_resource_plan(load_prediction=predictor_output)

    summary = build_summary(city, predictor_output, pollution_output, festival_output, disease_output)

    return {
        "city": city,
        "date": date,
        "data": data_payload,
        "pollution": pollution_output,
        "festival": festival_output,
        "disease": disease_output,
        "prediction": predictor_output,
        "operations": ops_output,
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def build_summary(
    city: str,
    prediction: Dict[str, Any],
    pollution: Dict[str, Any],
    festival: Dict[str, Any],
    disease: Dict[str, Any],
) -> str:
    """Generate a natural language summary."""
    loads = prediction.get("loads", {})
    pollution_impact = pollution.get("pollution_impact", {})
    festival_impact = festival.get("festival_impact", {})
    disease_impact = disease.get("disease_impact", {})

    parts = [
        f"For {city}, expected OPD load is {loads.get('opd', 'N/A')} patients and emergency load {loads.get('emergency', 'N/A')} patients.",
        f"ICU usage projected at {loads.get('icu', 'N/A')} beds with {loads.get('ventilator', 'N/A')} ventilators.",
        f"Pollution risk: {pollution_impact.get('risk_level', 'Unknown')} driving a {pollution_impact.get('opd_surge_percent', 0)}% OPD surge.",
    ]
    if festival_impact.get("festival_name"):
        parts.append(
            f"Festival {festival_impact.get('festival_name')} contributes an additional {festival_impact.get('emergency_surge_percent', 0)}% emergency surge."
        )
    parts.append(
        f"Disease outlook severity score {disease_impact.get('severity_score', 0)} with focus on {', '.join(disease_impact.get('expected_patient_types', ['general cases']))}."
    )
    parts.append(f"Overall risk level is {prediction.get('risk_level', 'Moderate')}.")
    return " ".join(parts)


coordinator_agent = Agent(
    name="CoordinatorAgent",
    instructions=(
        "Coordinates data collection, pollution/festival/disease analysis, overall prediction, "
        "and operational planning. Returns consolidated JSON and narrative summary."
    ),
    tools=[run_prediction_pipeline],
)

if __name__ == "__main__":
    from nest import run

    run(coordinator_agent, port=8016)

