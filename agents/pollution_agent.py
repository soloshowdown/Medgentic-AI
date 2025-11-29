"""Pollution Agent - Predicts impact of pollution on hospital load."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from nest import Agent, tool


@tool
def predict_pollution_impact(pollution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Predict hospital surge based on pollution levels.
    
    Args:
        pollution_data: Dictionary with aqi, pm25, pm10, aqi_category
    
    Returns:
        Dictionary with predicted OPD and ICU surge
    """
    aqi = pollution_data.get('aqi', 50)
    pm25 = pollution_data.get('pm25', 0)
    pm10 = pollution_data.get('pm10', 0)
    category = pollution_data.get('aqi_category', 'Good')
    
    # Base surge calculations
    opd_surge = 0
    icu_surge = 0
    emergency_surge = 0
    
    # AQI-based impact
    if aqi > 300:  # Hazardous
        opd_surge = 0.5  # 50% increase
        icu_surge = 0.4
        emergency_surge = 0.6
    elif aqi > 200:  # Very Unhealthy
        opd_surge = 0.35
        icu_surge = 0.25
        emergency_surge = 0.4
    elif aqi > 150:  # Unhealthy
        opd_surge = 0.25
        icu_surge = 0.15
        emergency_surge = 0.3
    elif aqi > 100:  # Unhealthy for Sensitive
        opd_surge = 0.15
        icu_surge = 0.08
        emergency_surge = 0.2
    elif aqi > 50:  # Moderate
        opd_surge = 0.08
        icu_surge = 0.03
        emergency_surge = 0.1
    
    # PM2.5 specific impact (respiratory issues)
    if pm25 > 150:
        opd_surge += 0.2
        icu_surge += 0.15
    elif pm25 > 100:
        opd_surge += 0.1
        icu_surge += 0.08
    
    # PM10 impact (eye and throat irritation)
    if pm10 > 200:
        opd_surge += 0.1
        emergency_surge += 0.15
    
    # Cap surges
    opd_surge = min(1.0, opd_surge)
    icu_surge = min(0.8, icu_surge)
    emergency_surge = min(1.0, emergency_surge)
    
    # Expected patient types
    patient_types = []
    if aqi > 150:
        patient_types.append("Respiratory distress")
        patient_types.append("Asthma exacerbation")
        patient_types.append("COPD complications")
    if pm25 > 100:
        patient_types.append("Bronchitis")
        patient_types.append("Pneumonia risk")
    if aqi > 200:
        patient_types.append("Cardiac complications")
        patient_types.append("Eye irritation")
    
    return {
        "pollution_impact": {
            "opd_surge_percent": round(opd_surge * 100, 2),
            "icu_surge_percent": round(icu_surge * 100, 2),
            "emergency_surge_percent": round(emergency_surge * 100, 2),
            "severity_score": min(1.0, aqi / 500),
            "risk_level": category,
            "expected_patient_types": patient_types,
            "recommendations": [
                "Increase respiratory medicine stock",
                "Prepare additional nebulizers",
                "Alert pulmonology department" if aqi > 200 else None,
                "Consider outdoor activity restrictions" if aqi > 300 else None
            ]
        }
    }


pollution_agent = Agent(
    name="PollutionAgent",
    instructions="Analyzes pollution data (AQI, PM2.5, PM10) and predicts impact on hospital load, particularly OPD and ICU surge. Uses rule-based logic with severity scoring.",
    tools=[predict_pollution_impact]
)

if __name__ == "__main__":
    from nest import run
    run(pollution_agent, port=8011)

