"""Festival Agent - Predicts festival-related hospital surges."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List
from nest import Agent, tool


@tool
def predict_festival_impact(festivals: List[Dict[str, Any]], date: str) -> Dict[str, Any]:
    """Predict hospital surge based on festivals.
    
    Args:
        festivals: List of festival dictionaries with name, date, type, impact_score
        date: Target date
    
    Returns:
        Dictionary with predicted surge metrics
    """
    if not festivals:
        return {
            "festival_impact": {
                "opd_surge_percent": 0,
                "emergency_surge_percent": 0,
                "icu_surge_percent": 0,
                "severity_score": 0,
                "festival_name": None,
                "expected_patient_types": [],
                "recommendations": []
            }
        }
    
    # Find the most impactful festival
    main_festival = max(festivals, key=lambda x: x.get('impact_score', 0))
    festival_name = main_festival.get('name', 'Unknown')
    impact_score = main_festival.get('impact_score', 0)
    days_away = main_festival.get('days_away', 0)
    
    # Adjust impact based on proximity
    proximity_factor = 1.0
    if abs(days_away) == 0:  # Exact day
        proximity_factor = 1.0
    elif abs(days_away) == 1:
        proximity_factor = 0.7
    elif abs(days_away) == 2:
        proximity_factor = 0.4
    
    # Festival-specific predictions
    opd_surge = 0
    emergency_surge = 0
    icu_surge = 0
    patient_types = []
    recommendations = []
    
    if "Diwali" in festival_name:
        # Firecracker injuries, burns, respiratory issues
        opd_surge = 0.4 * proximity_factor * impact_score
        emergency_surge = 0.6 * proximity_factor * impact_score
        icu_surge = 0.15 * proximity_factor * impact_score
        patient_types = [
            "Burn injuries",
            "Firecracker injuries",
            "Respiratory distress (smoke)",
            "Eye injuries",
            "Traffic accidents"
        ]
        recommendations = [
            "Stock burn treatment supplies",
            "Prepare emergency trauma team",
            "Increase respiratory medicine",
            "Alert ophthalmology department"
        ]
    
    elif "Holi" in festival_name:
        # Chemical eye injuries, respiratory issues, falls
        opd_surge = 0.35 * proximity_factor * impact_score
        emergency_surge = 0.5 * proximity_factor * impact_score
        icu_surge = 0.1 * proximity_factor * impact_score
        patient_types = [
            "Chemical eye injuries",
            "Skin allergies",
            "Respiratory irritation",
            "Falls and fractures"
        ]
        recommendations = [
            "Stock eye wash solutions",
            "Prepare dermatology team",
            "Increase antihistamines"
        ]
    
    elif "Ganpati" in festival_name:
        # Traffic accidents, noise-related issues, respiratory
        opd_surge = 0.3 * proximity_factor * impact_score
        emergency_surge = 0.45 * proximity_factor * impact_score
        icu_surge = 0.12 * proximity_factor * impact_score
        patient_types = [
            "Traffic accidents",
            "Respiratory issues (pollution)",
            "Noise-induced hearing issues"
        ]
        recommendations = [
            "Prepare trauma team",
            "Increase emergency staff",
            "Stock respiratory medications"
        ]
    
    elif "Eid" in festival_name or "Navratri" in festival_name:
        # General increase due to gatherings
        opd_surge = 0.25 * proximity_factor * impact_score
        emergency_surge = 0.35 * proximity_factor * impact_score
        icu_surge = 0.08 * proximity_factor * impact_score
        patient_types = [
            "Traffic accidents",
            "Food poisoning",
            "General emergencies"
        ]
        recommendations = [
            "Increase general emergency capacity",
            "Prepare for traffic accident surge"
        ]
    
    else:
        # Generic festival impact
        opd_surge = 0.2 * proximity_factor * impact_score
        emergency_surge = 0.3 * proximity_factor * impact_score
        icu_surge = 0.05 * proximity_factor * impact_score
        patient_types = ["General emergencies"]
        recommendations = ["Monitor emergency department"]
    
    return {
        "festival_impact": {
            "opd_surge_percent": round(opd_surge * 100, 2),
            "emergency_surge_percent": round(emergency_surge * 100, 2),
            "icu_surge_percent": round(icu_surge * 100, 2),
            "severity_score": impact_score * proximity_factor,
            "festival_name": festival_name,
            "days_away": days_away,
            "expected_patient_types": patient_types,
            "recommendations": recommendations
        }
    }


festival_agent = Agent(
    name="FestivalAgent",
    instructions="Analyzes festival calendar data and predicts hospital surge based on festival type. Considers firecracker injuries, traffic accidents, respiratory issues, and other festival-related health impacts.",
    tools=[predict_festival_impact]
)

if __name__ == "__main__":
    from nest import run
    run(festival_agent, port=8012)

