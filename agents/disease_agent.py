"""Disease Agent - Analyzes seasonal epidemics and disease patterns."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from nest import Agent, tool


@tool
def analyze_disease_season(health_data: Dict[str, Any], date: str) -> Dict[str, Any]:
    """Analyze disease seasonality and predict impact.
    
    Args:
        health_data: Dictionary with disease risk scores
        date: Target date
    
    Returns:
        Dictionary with disease impact predictions
    """
    month = int(date.split("-")[1])
    
    dengue_risk = health_data.get('dengue_risk', 0.3)
    viral_fever_risk = health_data.get('viral_fever_risk', 0.3)
    h1n1_risk = health_data.get('h1n1_risk', 0.2)
    
    # Calculate overall disease severity score
    max_risk = max(dengue_risk, viral_fever_risk, h1n1_risk)
    avg_risk = (dengue_risk + viral_fever_risk + h1n1_risk) / 3
    
    # Predict surge based on disease risks
    opd_surge = 0
    emergency_surge = 0
    icu_surge = 0
    patient_types = []
    recommendations = []
    
    # Dengue impact (monsoon season)
    if dengue_risk > 0.6:
        opd_surge += 0.3 * dengue_risk
        emergency_surge += 0.4 * dengue_risk
        icu_surge += 0.25 * dengue_risk
        patient_types.append("Dengue fever")
        patient_types.append("Dengue hemorrhagic fever")
        recommendations.append("Stock platelet concentrates")
        recommendations.append("Prepare dengue testing kits")
        recommendations.append("Alert hematology department")
    
    # Viral fever impact (winter season)
    if viral_fever_risk > 0.5:
        opd_surge += 0.25 * viral_fever_risk
        emergency_surge += 0.2 * viral_fever_risk
        icu_surge += 0.1 * viral_fever_risk
        patient_types.append("Viral fever")
        patient_types.append("Upper respiratory infections")
        recommendations.append("Increase antipyretics stock")
        recommendations.append("Prepare isolation beds")
    
    # H1N1 impact (winter/spring)
    if h1n1_risk > 0.4:
        opd_surge += 0.2 * h1n1_risk
        emergency_surge += 0.3 * h1n1_risk
        icu_surge += 0.35 * h1n1_risk  # H1N1 can be severe
        patient_types.append("H1N1 influenza")
        patient_types.append("Severe respiratory distress")
        recommendations.append("Stock oseltamivir (Tamiflu)")
        recommendations.append("Prepare ventilator capacity")
        recommendations.append("Alert infectious disease department")
    
    # Seasonal adjustments
    if month in [6, 7, 8, 9, 10]:  # Monsoon
        # Additional waterborne diseases
        opd_surge += 0.1
        patient_types.append("Waterborne diseases")
        recommendations.append("Monitor water quality")
    
    # Cap surges
    opd_surge = min(0.8, opd_surge)
    emergency_surge = min(0.7, emergency_surge)
    icu_surge = min(0.6, icu_surge)
    
    # Overall severity score
    severity_score = max_risk * 0.5 + avg_risk * 0.5
    
    return {
        "disease_impact": {
            "opd_surge_percent": round(opd_surge * 100, 2),
            "emergency_surge_percent": round(emergency_surge * 100, 2),
            "icu_surge_percent": round(icu_surge * 100, 2),
            "severity_score": round(severity_score, 3),
            "dengue_risk": round(dengue_risk, 3),
            "viral_fever_risk": round(viral_fever_risk, 3),
            "h1n1_risk": round(h1n1_risk, 3),
            "season": get_season(month),
            "expected_patient_types": list(set(patient_types)),  # Remove duplicates
            "recommendations": list(set(recommendations))
        }
    }


def get_season(month: int) -> str:
    """Get season name from month."""
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon"


disease_agent = Agent(
    name="DiseaseAgent",
    instructions="Analyzes seasonal disease patterns (Dengue, H1N1, viral fever) and predicts hospital surge. Uses historical patterns and seasonal factors to calculate severity scores.",
    tools=[analyze_disease_season]
)

if __name__ == "__main__":
    from nest import run
    run(disease_agent, port=8013)

